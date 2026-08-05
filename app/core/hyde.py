import logging
from typing import List
from app.core.generation import generate_answer

logger = logging.getLogger(__name__)

class HyDERetriever:
    """
    HyDE Engine: Hypothetical Document Embeddings.
    Generates a candidate hypothetical answer to align query embeddings
    with document chunk embeddings.
    """
    def generate_hypothetical_document(self, query: str) -> str:
        prompt_ctx = ["Generative hypothetical document synthesis mode."]
        hypothetical_doc = generate_answer(
            question=f"Write a detailed technical document passage that answers: '{query}'",
            contexts=prompt_ctx
        )
        return hypothetical_doc

hyde_engine = HyDERetriever()
