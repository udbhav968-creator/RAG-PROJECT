import logging
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

def _get_llm(model_name: str = None):
    target_model = model_name or settings.MODEL_NAME
    key = (settings.OPENAI_API_KEY or "").strip()
    if key and len(key) > 15 and key.startswith("sk-") and "your_" not in key:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=target_model,
                openai_api_key=key,
                temperature=0.2
            )
        except Exception as e:
            logger.warning(f"Failed to initialize ChatOpenAI ({target_model}): {e}")
    return None


def generate_answer(question: str, contexts: List[str], model_name: str = None) -> str:
    if not contexts:
        return "I don't have enough information to answer that based on the provided documents."

    context_str = "\n\n---\n\n".join(contexts)
    llm = _get_llm(model_name)
    
    if llm:
        try:
            from langchain.prompts import PromptTemplate
            from langchain.schema import HumanMessage, SystemMessage
            prompt = PromptTemplate(
                template="""You are a helpful assistant that answers questions based strictly on the given context.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:""",
                input_variables=["context", "question"]
            )
            formatted = prompt.format(context=context_str, question=question)
            messages = [
                SystemMessage(content="You are a truthful assistant that only uses the provided context."),
                HumanMessage(content=formatted)
            ]
            response = llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            logger.warning(f"ChatOpenAI invocation failed: {e}. Using fallback generator.")

    # Fallback context-grounded generator
    relevant_sentences = []
    q_words = set(question.lower().split())
    for ctx in contexts:
        for sent in ctx.split('.'):
            sent_clean = sent.strip()
            if not sent_clean:
                continue
            s_words = set(sent_clean.lower().split())
            if len(q_words.intersection(s_words)) >= 1:
                relevant_sentences.append(sent_clean)
                
    if relevant_sentences:
        summary = ". ".join(relevant_sentences[:3])
        if not summary.endswith('.'):
            summary += '.'
        return f"Based on the context: {summary}"
    else:
        return f"Based on the retrieved context: {contexts[0][:250]}..."