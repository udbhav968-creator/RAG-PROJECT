import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from app.api.v1.endpoints import query, ingest
from app.core.retrieval import init_pinecone, get_all_documents
from app.core.rag_pipeline import rag_pipeline
from app.utils.logging import setup_logging
from app.utils.metrics import metrics
from app.config import settings
from app.models import HealthResponse

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Industrial RAG with AI Detection & Correction",
    description="Enterprise Retrieval-Augmented Generation system with multi-attempt LLM faithfulness evaluation & query self-correction.",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_pinecone()
    logger.info("Application started successfully.")
    
    # Seed initial knowledge base if empty so users can test immediately
    docs = get_all_documents()
    if not docs:
        logger.info("Seeding initial industrial knowledge base documents...")
        sample_doc_1 = (
            "The Industrial RAG Engine (v2.0) is designed for fault-tolerant enterprise document intelligence. "
            "It features an iterative self-correction loop that evaluates faithfulness score of generated answers. "
            "If the initial score falls below 0.70, the system automatically rephrases the query and retrieves expanded context. "
            "The system supports both Pinecone Vector Indexing and an in-memory fallback vector store."
        )
        sample_doc_2 = (
            "Celery distributed tasks handle background document ingestion and async query execution via Redis brokers. "
            "Cache hits are served instantly via Redis or local memory cache with a default TTL of 3600 seconds. "
            "Prometheus metrics track latency, cache hit ratios, and average self-correction attempt counts."
        )
        rag_pipeline.ingest_document_text("INDUSTRIAL_SPEC_001", sample_doc_1)
        rag_pipeline.ingest_document_text("ARCHITECTURE_GUIDE_002", sample_doc_2)
        logger.info("Seed documents ingested successfully.")

from app.api.v1.endpoints import query, ingest, audit, graph

# Mount API Routers
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
app.include_router(audit.router, prefix="/api/v1", tags=["audit"])
app.include_router(graph.router, prefix="/api/v1", tags=["graph"])

@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
async def health():
    summary = metrics.get_summary()
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        vector_store="pinecone" if settings.PINECONE_API_KEY else "in-memory-fallback",
        redis_status="active",
        llm_provider="openai" if settings.OPENAI_API_KEY else "mock-fallback",
        uptime_seconds=summary["uptime_seconds"]
    )

@app.get("/metrics", tags=["monitoring"])
async def get_metrics():
    return metrics.get_summary()

# Mount Static Dashboard UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Industrial RAG System API is running. Visit /docs for Swagger documentation."}