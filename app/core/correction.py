import re
import logging
from typing import List, Tuple, Dict
from app.config import settings
from app.core.retrieval import retrieve
from app.core.generation import generate_answer

logger = logging.getLogger(__name__)

def _get_evaluator_llm():
    if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 15 and settings.OPENAI_API_KEY.startswith("sk-"):
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.MODEL_NAME,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.0
            )
        except Exception as e:
            logger.warning(f"Failed to initialize evaluator ChatOpenAI: {e}")
    return None

def evaluate_faithfulness(question: str, answer: str, contexts: List[str]) -> Tuple[float, bool]:
    if not contexts or not answer:
        return 0.0, False

    llm = _get_evaluator_llm()
    if llm:
        try:
            from langchain.prompts import PromptTemplate
            context_str = "\n\n".join(contexts)
            prompt = PromptTemplate(
                template="""You are an expert evaluator. Given the context, question, and the generated answer,
rate the faithfulness of the answer to the context on a scale of 0 to 1, where 1 means the answer is fully supported by the context.
Only use the provided context; do not rely on external knowledge.

Context:
{context}

Question: {question}

Answer: {answer}

Faithfulness score (numeric, 0 to 1):""",
                input_variables=["context", "question", "answer"]
            )
            formatted = prompt.format(context=context_str, question=question, answer=answer)
            response = llm.invoke([("user", formatted)])
            score_text = response.content.strip()
            match = re.search(r"(\d+\.?\d*)", score_text)
            score = float(match.group(1)) if match else 0.0
            score = max(0.0, min(1.0, score))
            is_faithful = score >= settings.FAITHFULNESS_THRESHOLD
            return score, is_faithful
        except Exception as e:
            logger.warning(f"Evaluator LLM invocation failed: {e}. Using deterministic faithfulness scorer.")

    # Heuristic Faithfulness Scorer (Fallback)
    ans_words = set(re.findall(r'\w+', answer.lower()))
    if not ans_words:
        return 0.0, False
    
    ctx_words = set(re.findall(r'\w+', " ".join(contexts).lower()))
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "of", "and", "or", "to", "for", "with", "by", "that", "this", "it", "as", "based"}
    filtered_ans = ans_words - stop_words
    
    if not filtered_ans:
        return 0.8, True

    overlap = filtered_ans.intersection(ctx_words)
    score = round(len(overlap) / len(filtered_ans), 2)
    score = max(0.2, min(1.0, score + 0.25))
    is_faithful = score >= settings.FAITHFULNESS_THRESHOLD
    return score, is_faithful

def rephrase_query(question: str) -> str:
    llm = _get_evaluator_llm()
    if llm:
        try:
            from langchain.prompts import PromptTemplate
            prompt = PromptTemplate(
                template="""Given the original question, rephrase it to be more specific and likely to retrieve relevant information from a document corpus.
Return only the rephrased question.

Original: {question}
Rephrased:""",
                input_variables=["question"]
            )
            formatted = prompt.format(question=question)
            response = llm.invoke([("user", formatted)])
            return response.content.strip()
        except Exception as e:
            logger.warning(f"Rephrase LLM failed: {e}")

    # Fallback rephraser
    return f"Detailed background and key specifics regarding {question}"

def correct_answer(original_question: str, initial_contexts: List[str],
                   initial_answer: str, max_attempts: int) -> Dict:
    attempts = []
    current_question = original_question
    current_contexts = initial_contexts
    current_answer = initial_answer
    
    score, faithful = evaluate_faithfulness(original_question, current_answer, current_contexts)
    attempts.append({
        "attempt": 1,
        "query": current_question,
        "answer": current_answer,
        "faithfulness_score": score,
        "is_faithful": faithful
    })

    for attempt in range(2, max_attempts + 1):
        if faithful:
            break
        new_question = rephrase_query(current_question)
        new_contexts = retrieve(new_question, k=settings.TOP_K_RETRIEVAL)
        combined_contexts = list(dict.fromkeys(current_contexts + new_contexts))
        new_answer = generate_answer(new_question, combined_contexts)
        score, faithful = evaluate_faithfulness(new_question, new_answer, combined_contexts)
        attempts.append({
            "attempt": attempt,
            "query": new_question,
            "answer": new_answer,
            "faithfulness_score": score,
            "is_faithful": faithful
        })
        current_question = new_question
        current_contexts = combined_contexts
        current_answer = new_answer

    if faithful:
        final_answer = current_answer
        final_contexts = current_contexts
    else:
        best = max(attempts, key=lambda x: x["faithfulness_score"])
        final_answer = best["answer"]
        final_contexts = current_contexts

    return {
        "final_answer": final_answer,
        "contexts": final_contexts,
        "attempts": attempts,
        "success": faithful
    }