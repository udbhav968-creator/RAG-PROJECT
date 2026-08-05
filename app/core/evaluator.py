import re
import math
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RAGTriadEvaluator:
    """
    RAG Triad Evaluator: Computes Context Precision, Context Recall, Faithfulness,
    and Answer Relevance scores (0.0 to 1.0) for enterprise observability.
    """

    def evaluate_triad(self, question: str, contexts: List[str], answer: str) -> Dict[str, float]:
        if not answer or not contexts:
            return {
                "faithfulness": 0.0,
                "answer_relevance": 0.0,
                "context_precision": 0.0,
                "context_recall": 0.0,
                "triad_average": 0.0
            }

        faithfulness = self._calc_faithfulness(contexts, answer)
        relevance = self._calc_answer_relevance(question, answer)
        precision = self._calc_context_precision(question, contexts)
        recall = self._calc_context_recall(question, contexts)

        triad_avg = round((faithfulness + relevance + precision + recall) / 4.0, 3)

        return {
            "faithfulness": round(faithfulness, 3),
            "answer_relevance": round(relevance, 3),
            "context_precision": round(precision, 3),
            "context_recall": round(recall, 3),
            "triad_average": triad_avg
        }

    def _calc_faithfulness(self, contexts: List[str], answer: str) -> float:
        combined_ctx = " ".join(contexts).lower()
        sentences = [s.strip() for s in re.split(r'[.!?]', answer) if s.strip()]
        if not sentences:
            return 1.0

        supported = 0
        for sent in sentences:
            s_words = [w for w in re.findall(r'\w+', sent.lower()) if len(w) > 3]
            if not s_words:
                supported += 1
                continue
            matches = sum(1 for w in s_words if w in combined_ctx)
            if (matches / len(s_words)) >= 0.35:
                supported += 1

        return supported / len(sentences)

    def _calc_answer_relevance(self, question: str, answer: str) -> float:
        q_words = set(w for w in re.findall(r'\w+', question.lower()) if len(w) > 2)
        a_words = set(w for w in re.findall(r'\w+', answer.lower()) if len(w) > 2)
        if not q_words:
            return 1.0

        overlap = len(q_words.intersection(a_words)) / len(q_words)
        length_penalty = min(len(answer.split()) / 5.0, 1.0)
        return min(overlap * 0.7 + length_penalty * 0.3, 1.0)

    def _calc_context_precision(self, question: str, contexts: List[str]) -> float:
        q_words = set(w for w in re.findall(r'\w+', question.lower()) if len(w) > 2)
        if not q_words or not contexts:
            return 0.0

        relevant_ranks = []
        for rank, ctx in enumerate(contexts, start=1):
            ctx_words = set(re.findall(r'\w+', ctx.lower()))
            if len(q_words.intersection(ctx_words)) >= 1:
                relevant_ranks.append(rank)

        if not relevant_ranks:
            return 0.0

        precisions = [len([r for r in relevant_ranks if r <= rank]) / rank for rank in relevant_ranks]
        return sum(precisions) / len(relevant_ranks)

    def _calc_context_recall(self, question: str, contexts: List[str]) -> float:
        q_words = set(w for w in re.findall(r'\w+', question.lower()) if len(w) > 3)
        if not q_words:
            return 1.0

        combined_ctx = " ".join(contexts).lower()
        found = sum(1 for w in q_words if w in combined_ctx)
        return found / len(q_words)

triad_evaluator = RAGTriadEvaluator()
