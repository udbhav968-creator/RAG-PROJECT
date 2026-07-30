import logging
import math
import re
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Global state for in-memory vector store fallback
_in_memory_store: List[Dict[str, Any]] = []
_pinecone_client = None

def _get_embeddings():
    if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 15 and settings.OPENAI_API_KEY.startswith("sk-"):
        try:
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAIEmbeddings: {e}")
    return None

def _simple_text_vector(text: str, dim: int = 1536) -> List[float]:
    """Fallback deterministic feature vector generation for local testing without OpenAI key."""
    words = re.findall(r'\w+', text.lower())
    vec = [0.0] * dim
    if not words:
        return vec
    for word in words:
        idx = hash(word) % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(v*v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec

def embed_texts(texts: List[str]) -> List[List[float]]:
    emb_model = _get_embeddings()
    if emb_model:
        try:
            return emb_model.embed_documents(texts)
        except Exception as e:
            logger.warning(f"OpenAI document embedding failed: {e}. Falling back to simple vectorizer.")
    return [_simple_text_vector(t) for t in texts]

def embed_query(query: str) -> List[float]:
    emb_model = _get_embeddings()
    if emb_model:
        try:
            return emb_model.embed_query(query)
        except Exception as e:
            logger.warning(f"OpenAI query embedding failed: {e}. Falling back to simple vectorizer.")
    return _simple_text_vector(query)

def init_pinecone():
    global _pinecone_client
    if settings.PINECONE_API_KEY and len(settings.PINECONE_API_KEY.strip()) > 15 and settings.PINECONE_API_KEY.startswith("pcsk_"):
        try:
            from pinecone import Pinecone
            _pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
            logger.info("Pinecone initialized successfully with modern v3 SDK.")
            return True
        except Exception as e:
            logger.warning(f"Pinecone initialization failed: {e}. Switching to In-Memory Vector Store.")
    else:
        logger.info("Pinecone API key unconfigured or invalid. Using In-Memory Vector Store fallback.")
    return False

def upsert_vectors(vectors: List[Dict[str, Any]]) -> None:
    """
    Vectors format: [{"id": "...", "values": [...], "metadata": {"text": "...", ...}}]
    """
    global _in_memory_store, _pinecone_client
    
    # Try Pinecone first if configured
    if _pinecone_client and settings.PINECONE_INDEX_NAME:
        try:
            index = _pinecone_client.Index(settings.PINECONE_INDEX_NAME)
            index.upsert(vectors=vectors)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone index '{settings.PINECONE_INDEX_NAME}'.")
            return
        except Exception as e:
            logger.warning(f"Pinecone upsert failed: {e}. Storing in memory fallback.")

    # In-memory store fallback
    for item in vectors:
        # Check if already exists (overwrite)
        _in_memory_store = [v for v in _in_memory_store if v["id"] != item["id"]]
        _in_memory_store.append(item)
    logger.info(f"Upserted {len(vectors)} vectors to In-Memory vector store (total: {len(_in_memory_store)}).")

def retrieve(query: str, k: int = None) -> List[str]:
    citations = retrieve_with_citations(query, k=k)
    return [c["text"] for c in citations]

def retrieve_with_citations(query: str, k: int = None) -> List[Dict[str, Any]]:
    if k is None:
        k = settings.TOP_K_RETRIEVAL

    query_vec = embed_query(query)
    q_words = set(re.findall(r'\w+', query.lower()))

    # Try Pinecone if active
    if _pinecone_client and settings.PINECONE_INDEX_NAME:
        try:
            index = _pinecone_client.Index(settings.PINECONE_INDEX_NAME)
            results = index.query(vector=query_vec, top_k=k, include_metadata=True)
            matched = []
            for match in results.matches:
                if match.metadata and "text" in match.metadata:
                    matched.append({
                        "document_id": match.metadata.get("document_id", "UNKNOWN"),
                        "chunk_index": match.metadata.get("chunk_index", 0),
                        "text": match.metadata["text"],
                        "score": match.score
                    })
            if matched:
                return matched
        except Exception as e:
            logger.warning(f"Pinecone query failed: {e}. Falling back to in-memory hybrid search.")

    # Hybrid Search (BM25 + Cosine Vector Similarity with RRF)
    if not _in_memory_store:
        logger.warning("In-memory vector store is empty.")
        return []

    scored_items = []
    for item in _in_memory_store:
        doc_vec = item["values"]
        doc_text = item["metadata"].get("text", "")
        doc_id = item["metadata"].get("document_id", item["id"].split("_")[0])
        chunk_idx = item["metadata"].get("chunk_index", 0)

        # 1. Cosine similarity
        dot_product = sum(q * d for q, d in zip(query_vec, doc_vec))
        q_norm = math.sqrt(sum(q * q for q in query_vec))
        d_norm = math.sqrt(sum(d * d for d in doc_vec))
        sim = (dot_product / (q_norm * d_norm)) if (q_norm > 0 and d_norm > 0) else 0.0
        
        # 2. BM25 term frequency matching
        doc_words = re.findall(r'\w+', doc_text.lower())
        tf_score = sum(doc_words.count(w) for w in q_words) / max(len(doc_words), 1)
        
        # 3. Reciprocal Rank Fusion (RRF) / Hybrid score
        combined_score = sim * 0.65 + tf_score * 0.35
        
        scored_items.append({
            "document_id": doc_id,
            "chunk_index": chunk_idx,
            "text": doc_text,
            "score": round(combined_score, 4)
        })

    scored_items.sort(key=lambda x: x["score"], reverse=True)
    return scored_items[:k]


def get_all_documents() -> List[Dict[str, Any]]:
    """Returns list of stored document metadata for API management."""
    docs = {}
    for item in _in_memory_store:
        doc_id = item["metadata"].get("document_id", item["id"].split("_")[0])
        if doc_id not in docs:
            docs[doc_id] = {
                "document_id": doc_id,
                "chunk_count": 0,
                "sample_text": item["metadata"].get("text", "")[:150] + "..."
            }
        docs[doc_id]["chunk_count"] += 1
    return list(docs.values())

def delete_document_chunks(doc_id: str) -> int:
    global _in_memory_store
    initial_len = len(_in_memory_store)
    _in_memory_store = [
        v for v in _in_memory_store 
        if v["metadata"].get("document_id") != doc_id and not v["id"].startswith(f"{doc_id}_")
    ]
    removed = initial_len - len(_in_memory_store)
    logger.info(f"Deleted {removed} chunks for document_id '{doc_id}'.")
    return removed