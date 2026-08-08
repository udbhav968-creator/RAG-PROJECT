import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Canonical Entity Alias Mappings
ENTITY_ALIASES = {
    "oai": "OpenAI",
    "openai inc": "OpenAI",
    "openai corp": "OpenAI",
    "fastapi framework": "FastAPI",
    "pinecone vector db": "Pinecone"
}

class GraphEntityDisambiguator:
    """
    Knowledge Graph Entity Auto-Disambiguation Engine:
    Resolves entity aliases and acronyms into unified canonical entity nodes.
    """
    def disambiguate_entity(self, entity_name: str) -> str:
        cleaned = entity_name.lower().strip()
        canonical = ENTITY_ALIASES.get(cleaned, entity_name)
        if canonical != entity_name:
            logger.info(f"Graph Disambiguator resolved alias '{entity_name}' -> '{canonical}'")
        return canonical

graph_disambiguator = GraphEntityDisambiguator()
