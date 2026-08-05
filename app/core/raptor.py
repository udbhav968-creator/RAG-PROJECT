import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RAPTORSummarizer:
    """
    RAPTOR Indexer: Recursive Abstractive Processing for Tree-Organized Retrieval.
    Builds multi-level summary trees of documents to answer high-level thematic queries.
    """
    def __init__(self):
        self.tree_levels: Dict[str, Dict[int, List[str]]] = {}  # doc_id -> {level -> [summaries]}

    def build_raptor_tree(self, doc_id: str, chunks: List[str]) -> Dict[int, List[str]]:
        level_0 = chunks
        level_1 = []

        # Group level_0 chunks into clusters of 3 for Level 1 section summaries
        for i in range(0, len(level_0), 3):
            cluster = level_0[i:i+3]
            combined = " ".join(cluster)
            # Heuristic abstractive summary generator for level 1
            words = [w for w in re.findall(r'\w+', combined) if len(w) > 4]
            key_terms = list(set(words))[:8]
            summary_1 = f"Section Summary [{doc_id} L1]: Key topics include {', '.join(key_terms)}. Overview: {combined[:200]}..."
            level_1.append(summary_1)

        # Level 2 Document Theme Summary
        combined_l1 = " ".join(level_1)
        all_words = list(set([w for w in re.findall(r'\w+', combined_l1) if len(w) > 4]))[:12]
        level_2 = [f"Global Theme Summary [{doc_id} L2]: Overarching themes cover {', '.join(all_words)}."]

        tree = {
            0: level_0,
            1: level_1,
            2: level_2
        }
        self.tree_levels[doc_id] = tree
        return tree

    def get_raptor_summaries(self, query: str) -> List[str]:
        matched_summaries = []
        q_words = set(re.findall(r'\w+', query.lower()))

        for doc_id, tree in self.tree_levels.items():
            for level in [2, 1]:  # High level summaries first
                for summary in tree.get(level, []):
                    s_words = set(re.findall(r'\w+', summary.lower()))
                    if len(q_words.intersection(s_words)) >= 1:
                        matched_summaries.append(summary)

        return matched_summaries[:3]

raptor_engine = RAPTORSummarizer()
