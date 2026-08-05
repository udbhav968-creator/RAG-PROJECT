import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AgenticQueryRouter:
    """
    Agentic Router: Classifies incoming queries and routes them to the optimal execution tool.
    Tools: Vector Search, GraphRAG Relational Search, Code Sandbox Python Execution, or Direct LLM.
    """
    def route_query(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()

        # Math / Analytical calculation query
        if any(term in q_lower for term in ["calculate", "sum", "average", "compute", "+", "*", "/"]):
            return {
                "selected_tool": "code_sandbox",
                "reason": "Query contains mathematical calculation directives."
            }

        # Multi-hop relational graph query
        if any(term in q_lower for term in ["depend", "relationship", "connect", "affect", "impact", "cause", "trigger"]):
            return {
                "selected_tool": "graph_rag",
                "reason": "Query requires multi-hop entity-relationship graph traversal."
            }

        # Default: Dense Vector + BM25 Hybrid Search
        return {
            "selected_tool": "hybrid_vector_search",
            "reason": "Query requires semantic document retrieval."
        }

agent_router = AgenticQueryRouter()
