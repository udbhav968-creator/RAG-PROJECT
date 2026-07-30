import logging
from typing import Dict, Any, List, Optional
from app.config import settings
from app.core.retrieval import retrieve, embed_texts, upsert_vectors
from app.core.generation import generate_answer
from app.core.correction import correct_answer
from app.cache.redis_client import get_cached_answer_sync, set_cached_answer_sync
from app.utils.metrics import metrics

logger = logging.getLogger(__name__)

def _split_text_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_text(text)
    except Exception:
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            return splitter.split_text(text)
        except Exception:
            logger.info("Using lightweight character text splitter fallback.")
            chunks = []
            start = 0
            text_len = len(text)
            step = chunk_size - chunk_overlap if chunk_size > chunk_overlap else chunk_size
            while start < text_len:
                end = min(start + chunk_size, text_len)
                chunks.append(text[start:end])
                start += step
                if start >= text_len or end == text_len:
                    break
            return chunks if chunks else [text]

from app.core.retrieval import retrieve, retrieve_with_citations, embed_texts, upsert_vectors

class RAGPipeline:
    def __init__(self):
        logger.info("Initializing RAGPipeline engine.")

    def run_query(self, question: str, max_attempts: Optional[int] = None, model_name: str = None) -> Dict[str, Any]:
        if max_attempts is None:
            max_attempts = settings.MAX_CORRECTION_ATTEMPTS
        target_model = model_name or settings.MODEL_NAME

        # Check Cache
        cached = get_cached_answer_sync(question)
        if cached:
            audit_id = metrics.record_query(
                question=question,
                final_answer=cached.get("final_answer", ""),
                success=cached.get("success", True),
                faithfulness_score=cached["attempts"][-1]["faithfulness_score"] if cached.get("attempts") else 1.0,
                attempts_count=len(cached.get("attempts", [1])),
                from_cache=True,
                model_name=target_model
            )
            cached["question"] = question
            cached["audit_id"] = audit_id
            return cached

        # Step 1: Initial Hybrid Retrieval with Structured Citations
        citation_items = retrieve_with_citations(question, k=settings.TOP_K_RETRIEVAL)
        contexts = [c["text"] for c in citation_items]
        
        # Step 2: Initial Generation
        initial_answer = generate_answer(question, contexts, model_name=target_model)
        
        # Step 3: Faithfulness Evaluation & Iterative Self-Correction
        result = correct_answer(question, contexts, initial_answer, max_attempts)
        result["question"] = question
        
        # Add citations structure
        result["citations"] = [
            {
                "document_id": c["document_id"],
                "chunk_index": c["chunk_index"],
                "text_snippet": c["text"][:150] + "..."
            }
            for c in citation_items
        ]

        # Save to Cache & Metrics Audit Log
        set_cached_answer_sync(question, result)
        final_faithfulness = result["attempts"][-1]["faithfulness_score"] if result.get("attempts") else 0.0
        attempts_len = len(result.get("attempts", []))
        audit_id = metrics.record_query(
            question=question,
            final_answer=result.get("final_answer", ""),
            success=result.get("success", False),
            faithfulness_score=final_faithfulness,
            attempts_count=attempts_len,
            from_cache=False,
            model_name=target_model
        )
        result["audit_id"] = audit_id

        return result

    def ingest_document_text(self, document_id: str, content: str, chunk_size: int = 500, chunk_overlap: int = 50) -> Dict[str, Any]:
        chunks = _split_text_chunks(content, chunk_size, chunk_overlap)
        
        if not chunks:
            chunks = [content]

        embeddings = embed_texts(chunks)
        vectors = [
            {
                "id": f"{document_id}_{i}",
                "values": emb,
                "metadata": {
                    "text": chunk,
                    "document_id": document_id,
                    "chunk_index": i
                }
            }
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]

        upsert_vectors(vectors)
        metrics.record_ingestion(document_id, len(chunks))

        return {
            "status": "success",
            "document_id": document_id,
            "chunks_processed": len(chunks),
            "sample_chunk": chunks[0][:150] + "..." if chunks else ""
        }

rag_pipeline = RAGPipeline()