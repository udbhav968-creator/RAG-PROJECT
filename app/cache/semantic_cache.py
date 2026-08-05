import logging
import math
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class SemanticVectorCache:
    """
    Sub-Millisecond Semantic Vector Cache: Computes cosine similarity between
    query vectors to serve cached RAG answers instantly if similarity > 0.92.
    """
    def __init__(self, similarity_threshold: float = 0.92):
        self.threshold = similarity_threshold
        self.entries: List[Dict[str, Any]] = []  # [{query, query_vector, response}]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def get_semantic_match(self, query_vec: List[float]) -> Optional[Dict[str, Any]]:
        best_score = 0.0
        best_entry = None

        for entry in self.entries:
            score = self._cosine_similarity(query_vec, entry["query_vector"])
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score >= self.threshold:
            logger.info(f"Semantic Cache HIT (similarity score: {best_score:.4f})")
            res = dict(best_entry["response"])
            res["from_semantic_cache"] = True
            res["similarity_score"] = round(best_score, 4)
            return res

        return None

    def store_semantic_entry(self, query: str, query_vec: List[float], response: Dict[str, Any]):
        self.entries.append({
            "query": query,
            "query_vector": query_vec,
            "response": response
        })

semantic_cache = SemanticVectorCache()
