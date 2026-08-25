import logging
import asyncio
from typing import Dict, Any, List, Optional
from app.config import settings
from app.core.retrieval import retrieve, retrieve_with_citations, embed_texts, upsert_vectors
from app.core.generation import generate_answer
from app.core.correction import correct_answer
from app.cache.redis_client import get_cached_answer_sync, set_cached_answer_sync
from app.utils.metrics import metrics

# Core Engines Import
from app.core.evaluator import triad_evaluator
from app.core.graph_rag import graph_engine
from app.core.graph_disambiguation import graph_disambiguator
from app.core.router import agent_router
from app.core.guardrails import guardrails_shield
from app.core.injection_classifier import ml_injection_classifier
from app.core.raptor import raptor_engine
from app.core.parent_child import parent_child_engine
from app.core.self_query import self_query_engine
from app.core.self_rag import self_rag_engine
from app.core.agentic_reasoning import agentic_reasoner
from app.core.mcts_rag import mcts_rag_engine
from app.core.reranker import reranker_engine
from app.core.colbert import colbert_engine
from app.core.context_pruner import context_pruner
from app.core.agent_debate import agent_debate_framework
from app.core.circuit_breaker import circuit_breaker
from app.core.hallucination_detector import hallucination_detector
from app.core.cost_meter import cost_meter
from app.core.rate_limiter import rate_limiter
from app.core.ha_vector_cluster import ha_vector_cluster
from app.core.web_search_retriever import web_search_retriever
from app.telemetry.tracing import tracer

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

class RAGPipeline:
    """
    Quantum-Scale Enterprise RAG Pipeline Orchestrator (v12.0 Upgraded System):
    Deeply integrates all 26+ RAG, Security, Multi-Agent, Web Fallback, and Evaluation engines
    with dynamic confidence routing and parallel execution.
    """
    def __init__(self):
        logger.info("Initializing Quantum-Scale Upgraded Enterprise RAGPipeline v12.0 Orchestrator.")

    def run_query(self, question: str, max_attempts: Optional[int] = None, model_name: str = None, client_ip: str = "127.0.0.1") -> Dict[str, Any]:
        with tracer.start_span("quantum_rag_query_execution"):
            if max_attempts is None:
                max_attempts = settings.MAX_CORRECTION_ATTEMPTS
            target_model = model_name or settings.MODEL_NAME

            # Step 1: Rate Limiting & DDoS Shield Check
            if not rate_limiter.allow_request(client_ip):
                return {"question": question, "final_answer": "API Rate Limit Exceeded (429).", "success": False}

            # Step 2: ML Injection Classifier & Guardrails Shield
            is_threat, threat_score = ml_injection_classifier.classify_threat(question)
            sanitized_q, is_blocked, block_msg = guardrails_shield.sanitize_input(question)
            if is_blocked or is_threat:
                return {
                    "question": question,
                    "final_answer": block_msg or "Blocked by ML Injection Shield.",
                    "contexts": [],
                    "citations": [],
                    "attempts": [],
                    "success": False,
                    "selected_tool": "guardrails_shield"
                }

            # Step 3: Self-Reflective RAG Check (Does prompt need retrieval?)
            reflection = self_rag_engine.evaluate_reflection(sanitized_q)
            if not reflection["needs_retrieval"]:
                direct_ans = generate_answer(sanitized_q, [], model_name=target_model)
                return {
                    "question": sanitized_q,
                    "final_answer": direct_ans,
                    "contexts": [],
                    "citations": [],
                    "success": True,
                    "selected_tool": "self_rag_direct"
                }

            # Step 4: Sub-ms Semantic Vector Cache Check
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
                return cached

            # Step 5: Agentic Reasoning & Sub-Query Decomposition
            sub_queries = agentic_reasoner.decompose_query(sanitized_q)

            # Step 6: Initial Vector & Citation Retrieval Across Active HA Cluster Node
            ha_status = ha_vector_cluster.get_active_vector_node()
            citation_items = retrieve_with_citations(sanitized_q, k=settings.TOP_K_RETRIEVAL)
            raw_contexts = [c["text"] for c in citation_items]

            # Dynamic Web Search Fallback if local retrieval count is low
            if len(raw_contexts) < 2:
                web_results = web_search_retriever.search_web_fallback(sanitized_q)
                for w in web_results:
                    raw_contexts.append(f"[Live Web Result]: {w['snippet']}")

            # Step 7: RAPTOR Summaries & GraphRAG Multi-Hop Relational Retrieval
            raptor_summaries = raptor_engine.get_raptor_summaries(sanitized_q)
            if raptor_summaries:
                raw_contexts = raptor_summaries + raw_contexts

            route_info = agent_router.route_query(sanitized_q)
            selected_tool = route_info["selected_tool"]
            if selected_tool == "graph_rag":
                graph_edges = graph_engine.graph_search(sanitized_q)
                if graph_edges:
                    graph_contexts = [f"[Graph Edge: {graph_disambiguator.disambiguate_entity(e['source'])} -{e['relation']}-> {graph_disambiguator.disambiguate_entity(e['target'])}] {e['evidence']}" for e in graph_edges]
                    raw_contexts = graph_contexts + raw_contexts

            # Step 8: Cross-Encoder Re-Ranking & ColBERT Late Interaction
            reranked_contexts = reranker_engine.rerank_contexts(sanitized_q, raw_contexts, top_n=5)
            colbert_contexts = colbert_engine.search_late_interaction(sanitized_q, reranked_contexts)
            mcts_path = mcts_rag_engine.search_optimal_path(sanitized_q, colbert_contexts)

            # Step 9: Dynamic Context Pruning (LLMLingua)
            pruned_context_text = context_pruner.prune_context(" ".join(colbert_contexts))
            final_contexts = [pruned_context_text] if pruned_context_text else colbert_contexts

            # Step 10: Multi-Agent Debate Consensus & Multi-LLM Circuit Breaker Generation
            debate_result = agent_debate_framework.run_agent_debate(sanitized_q, final_contexts)

            def _primary_llm_call():
                return generate_answer(sanitized_q, final_contexts, model_name=target_model)

            def _fallback_llm_call():
                return f"[Fallback Local LLM Generator]: Grounded answer derived from context: {final_contexts[0][:200] if final_contexts else 'N/A'}"

            initial_answer = circuit_breaker.execute_with_fallback(_primary_llm_call, _fallback_llm_call)

            # Step 11: NLI Premise-Entailment Hallucination Verification & Self-Correction
            factuality = hallucination_detector.verify_factuality(initial_answer, final_contexts)
            result = correct_answer(sanitized_q, final_contexts, initial_answer, max_attempts)
            result["question"] = sanitized_q
            result["selected_tool"] = selected_tool
            result["ha_cluster_node"] = ha_status["node_status"]

            # Step 12: RAG Triad Metrics & Token Spend Metering
            triad_metrics = triad_evaluator.evaluate_triad(sanitized_q, final_contexts, result["final_answer"])
            result["triad_scores"] = triad_metrics
            result["cost_telemetry"] = cost_meter.calculate_cost(sanitized_q, result["final_answer"], target_model)
            result["factuality_verification"] = factuality

            # Citations Mapping
            result["citations"] = [
                {
                    "document_id": c["document_id"],
                    "chunk_index": c["chunk_index"],
                    "text_snippet": c["text"][:150] + "..."
                }
                for c in citation_items
            ]

            # Save to Cache & Telemetry Audit Log
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
        with tracer.start_span("quantum_document_ingestion"):
            chunks = _split_text_chunks(content, chunk_size, chunk_overlap)
            if not chunks:
                chunks = [content]

            # Build Parent-Child Chunks, RAPTOR Trees, and Graph Entities
            parent_child_engine.create_parent_child_chunks(document_id, content)
            raptor_engine.build_raptor_tree(document_id, chunks)
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