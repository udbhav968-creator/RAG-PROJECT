import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ParentChildChunker:
    """
    Parent-Child Chunking & Auto-Merging Engine: Creates small 150-word child chunks
    for sharp vector similarity matching, while preserving 1,000-word parent sections.
    """
    def __init__(self):
        self.parents_store: Dict[str, str] = {}  # parent_id -> parent_text

    def create_parent_child_chunks(self, doc_id: str, content: str, parent_size: int = 1000, child_size: int = 200) -> List[Dict[str, Any]]:
        words = content.split()
        chunks_data = []
        
        # Build Parent Sections
        parent_idx = 0
        for p_start in range(0, len(words), parent_size):
            parent_words = words[p_start : p_start + parent_size]
            parent_text = " ".join(parent_words)
            parent_id = f"{doc_id}_P{parent_idx}"
            self.parents_store[parent_id] = parent_text

            # Build Child Chunks inside this Parent
            child_idx = 0
            for c_start in range(0, len(parent_words), child_size):
                child_words = parent_words[c_start : c_start + child_size]
                child_text = " ".join(child_words)
                child_id = f"{parent_id}_C{child_idx}"

                chunks_data.append({
                    "child_id": child_id,
                    "parent_id": parent_id,
                    "child_text": child_text,
                    "doc_id": doc_id
                })
                child_idx += 1
            parent_idx += 1

        return chunks_data

    def auto_merge_parents(self, child_items: List[Dict[str, Any]]) -> List[str]:
        seen_parents = set()
        merged_contexts = []

        for item in child_items:
            parent_id = item.get("parent_id")
            if parent_id and parent_id in self.parents_store:
                if parent_id not in seen_parents:
                    seen_parents.add(parent_id)
                    merged_contexts.append(self.parents_store[parent_id])
            else:
                merged_contexts.append(item.get("child_text", item.get("text", "")))

        return merged_contexts

parent_child_engine = ParentChildChunker()
