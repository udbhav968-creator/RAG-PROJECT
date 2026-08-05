import re
import logging
from typing import List, Dict, Any, Set, Tuple

logger = logging.getLogger(__name__)

class KnowledgeGraphEngine:
    """
    Lightweight GraphRAG Engine: Extracts entities & relations from text chunks
    and provides multi-hop graph traversal retrieval for relational queries.
    """
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}  # entity_id -> {label, type, doc_id}
        self.edges: List[Dict[str, Any]] = []      # [{source, target, relation, doc_id}]

    def extract_and_add(self, doc_id: str, text: str) -> None:
        # Regex patterns for technical entities
        words = re.findall(r'[A-Z][a-zA-Z0-9_\-]{2,}', text)
        entities = list(set(words))

        for ent in entities:
            if ent not in self.nodes:
                self.nodes[ent] = {
                    "id": ent,
                    "type": "Entity",
                    "doc_id": doc_id
                }

        # Co-occurrence & relation extraction
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        for sent in sentences:
            sent_ents = [e for e in entities if e in sent]
            if len(sent_ents) >= 2:
                for i in range(len(sent_ents) - 1):
                    src, tgt = sent_ents[i], sent_ents[i+1]
                    if src != tgt:
                        rel_type = "RELATED_TO"
                        sent_lower = sent.lower()
                        if "depend" in sent_lower or "use" in sent_lower:
                            rel_type = "DEPENDS_ON"
                        elif "exceed" in sent_lower or "trigger" in sent_lower:
                            rel_type = "TRIGGERS"
                        elif "regulate" in sent_lower or "control" in sent_lower:
                            rel_type = "REGULATES"

                        self.edges.append({
                            "source": src,
                            "target": tgt,
                            "relation": rel_type,
                            "doc_id": doc_id,
                            "evidence": sent[:150]
                        })

    def graph_search(self, query: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        q_entities = [e for e in self.nodes if e.lower() in query.lower()]
        matched_edges = []

        if not q_entities:
            # Fallback: return sample edges if matching query words
            q_words = set(re.findall(r'\w+', query.lower()))
            for edge in self.edges:
                if any(w in edge["evidence"].lower() for w in q_words if len(w) > 3):
                    matched_edges.append(edge)
            return matched_edges[:5]

        # Multi-hop graph traversal
        visited_nodes: Set[str] = set(q_entities)
        current_layer = q_entities

        for depth in range(max_depth):
            next_layer = []
            for edge in self.edges:
                if edge["source"] in current_layer or edge["target"] in current_layer:
                    if edge not in matched_edges:
                        matched_edges.append(edge)
                    other = edge["target"] if edge["source"] in current_layer else edge["source"]
                    if other not in visited_nodes:
                        visited_nodes.add(other)
                        next_layer.append(other)
            current_layer = next_layer
            if not current_layer:
                break

        return matched_edges[:10]

    def get_graph_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "sample_nodes": list(self.nodes.keys())[:10],
            "sample_edges": self.edges[:5]
        }

graph_engine = KnowledgeGraphEngine()
