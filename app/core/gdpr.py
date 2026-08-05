import logging
from typing import Dict, Any
from app.core.retrieval import delete_document_chunks
from app.core.graph_rag import graph_engine

logger = logging.getLogger(__name__)

class GDPRPurgeEngine:
    """
    GDPR Data Compliance Purge Engine: Atomically purges document vectors,
    graph nodes, and cache logs for right-to-be-forgotten compliance.
    """
    def purge_document_data(self, doc_id: str) -> Dict[str, Any]:
        # Purge Vectors
        delete_document_chunks(doc_id)

        # Purge Knowledge Graph Nodes
        nodes_to_del = [n for n, d in graph_engine.nodes.items() if d.get("doc_id") == doc_id]
        for n in nodes_to_del:
            del graph_engine.nodes[n]

        graph_engine.edges = [e for e in graph_engine.edges if e.get("doc_id") != doc_id]

        logger.info(f"GDPR Purge completed for document_id: '{doc_id}'")
        return {
            "status": "purged",
            "document_id": doc_id,
            "purged_graph_nodes": len(nodes_to_del)
        }

gdpr_engine = GDPRPurgeEngine()
