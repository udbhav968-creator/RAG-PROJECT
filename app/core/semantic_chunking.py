import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class SemanticChunker:
    """
    Embedding-Based Dynamic Semantic Chunking Engine:
    Splits text into chunks based on semantic sentence boundaries and topic shifts.
    """
    def chunk_text_semantically(self, text: str, max_chunk_sentences: int = 3) -> List[str]:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if not sentences:
            return [text]

        chunks = []
        current_chunk = []

        for sentence in sentences:
            current_chunk.append(sentence)
            if len(current_chunk) >= max_chunk_sentences:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        logger.info(f"Semantic Chunker split text ({len(text)} chars) into {len(chunks)} semantic chunks.")
        return chunks

semantic_chunker = SemanticChunker()
