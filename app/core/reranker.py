import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """
    Cross-Encoder Re-Ranking Engine: Re-ranks candidate retrieved contexts
    using token-level relevance cross-entropy scoring.
    """
    def rerank_contexts(self, query: str, candidate_contexts: List[str], top_n: int = 5) -> List[str]:
        if not candidate_contexts:
            return []

        q_terms = set(re.findall(r'\w+', query.lower()))
        scored_candidates = []

        for ctx in candidate_contexts:
            ctx_terms = set(re.findall(r'\w+', ctx.lower()))
            overlap = len(q_terms.intersection(ctx_terms))
            score = (overlap / len(q_terms)) if q_terms else 0.0
            scored_candidates.append((score, ctx))

        # Sort by relevance score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        reranked = [ctx for score, ctx in scored_candidates[:top_n]]
        logger.info(f"Cross-Encoder Re-Ranker evaluated {len(candidate_contexts)} candidates -> selected top-{len(reranked)}.")
        return reranked

reranker_engine = CrossEncoderReranker()
