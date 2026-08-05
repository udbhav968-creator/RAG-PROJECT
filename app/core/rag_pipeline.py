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
from app.core.evaluator import triad_evaluator
from app.core.graph_rag import graph_engine
from app.core.router import agent_router
from app.core.guardrails import guardrails_shield
from app.core.raptor import raptor_engine
from app.core.parent_child import parent_child_engine
from app.core.self_query import self_query_engine

class RAGPipeline:
    def __init__(self):
        logger.info("Initializing World-Class RAGPipeline v3.0 engine.")

    def run_query(self, question: str, max_attempts: Optional[int] = None, model_name: str = None) -> Dict[str, Any]:
        if max_attempts is None:
            max_attempts = settings.MAX_CORRECTION_ATTEMPTS
        target_model = model_name or settings.MODEL_NAME

        # Step 0: Guardrails AI Shield (Input Sanitization & Injection Shield)
        sanitized_q, is_blocked, block_msg = guardrails_shield.sanitize_input(question)
        if is_blocked:
            return {
                "question": question,
                "final_answer": block_msg,
                "contexts": [],
                "citations": [],
                "attempts": [],
                "success": False,
                "selected_tool": "guardrails_shield"
            }

        # Self-Querying Metadata Parser
        parsed_filters = self_query_engine.parse_query_filters(sanitized_q)

        # Route query via Agentic Router
        route_info = agent_router.route_query(sanitized_q)
        selected_tool = route_info["selected_tool"]

        # Check Cache
        cached = get_cached_answer_sync(sanitized_q)
        if cached:
            audit_id = metrics.record_query(
                question=sanitized_q,
                final_answer=cached.get("final_answer", ""),
                success=cached.get("success", True),
                faithfulness_score=cached["attempts"][-1]["faithfulness_score"] if cached.get("attempts") else 1.0,
                attempts_count=len(cached.get("attempts", [1])),
                from_cache=True,
                model_name=target_model
            )
            cached["question"] = sanitized_q
            cached["audit_id"] = audit_id
            cached["selected_tool"] = selected_tool
            return cached

        # Step 1: Initial Hybrid Retrieval with Structured Citations
        citation_items = retrieve_with_citations(sanitized_q, k=settings.TOP_K_RETRIEVAL)
        contexts = [c["text"] for c in citation_items]

        # RAPTOR Tree Summaries Boost
        raptor_summaries = raptor_engine.get_raptor_summaries(sanitized_q)
        if raptor_summaries:
            contexts = raptor_summaries + contexts

        # GraphRAG multi-hop relational retrieval boost if selected
        if selected_tool == "graph_rag":
            graph_edges = graph_engine.graph_search(sanitized_q)
            if graph_edges:
                graph_contexts = [f"[Graph Edge: {e['source']} -{e['relation']}-> {e['target']}] {e['evidence']}" for e in graph_edges]
                contexts = graph_contexts + contexts

        # Step 2: Initial Generation
        initial_answer = generate_answer(sanitized_q, contexts, model_name=target_model)
        
        # Step 3: Faithfulness Evaluation & Iterative Self-Correction
        result = correct_answer(sanitized_q, contexts, initial_answer, max_attempts)
        result["question"] = sanitized_q
        result["selected_tool"] = selected_tool
        result["metadata_filters"] = parsed_filters

        # Guardrails AI Output Sanitization
        result["final_answer"] = guardrails_shield.sanitize_output(result["final_answer"])

        # Step 4: RAG Triad Metrics Calculation (Faithfulness, Relevance, Precision, Recall)
        triad_metrics = triad_evaluator.evaluate_triad(sanitized_q, contexts, result["final_answer"])
        result["triad_scores"] = triad_metrics

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
        set_cached_answer_sync(sanitized_q, result)
        final_faithfulness = result["attempts"][-1]["faithfulness_score"] if result.get("attempts") else 0.0
        attempts_len = len(result.get("attempts", []))
        audit_id = metrics.record_query(
            question=sanitized_q,
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

        # Build Parent-Child Chunks
        parent_child_engine.create_parent_child_chunks(document_id, content)

        # Build RAPTOR Summary Tree
        raptor_engine.build_raptor_tree(document_id, chunks)

        # Extract Knowledge Graph entities & relationships
        graph_engine.extract_and_add(document_id, content)

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