from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    question: str = Field(..., description="User's natural language query")
    max_attempts: Optional[int] = Field(None, description="Maximum self-correction attempts (default: 2)")
    model_name: Optional[str] = Field("gpt-4", description="Target LLM model (e.g. gpt-4, gpt-3.5-turbo, local)")
    provider: Optional[str] = Field("openai", description="Model provider (openai or local)")

class CorrectionAttempt(BaseModel):
    attempt: int
    query: str
    answer: str
    faithfulness_score: float
    is_faithful: bool

class CitationItem(BaseModel):
    document_id: str
    chunk_index: int
    text_snippet: str

class QueryResponse(BaseModel):
    question: str
    final_answer: str
    contexts: List[str]
    citations: List[CitationItem] = []
    attempts: List[CorrectionAttempt]
    success: bool
    audit_id: Optional[str] = None

class IngestRequest(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="Raw text content of the document")
    chunk_size: Optional[int] = Field(500, description="Text splitter chunk size")
    chunk_overlap: Optional[int] = Field(50, description="Text splitter chunk overlap")

class IngestResponse(BaseModel):
    status: str
    document_id: str
    chunks_processed: int
    sample_chunk: str

class DocumentItem(BaseModel):
    document_id: str
    chunk_count: int
    sample_text: str

class DocumentListResponse(BaseModel):
    total_documents: int
    documents: List[DocumentItem]

class AuditLogEntry(BaseModel):
    audit_id: str
    timestamp: float
    question: str
    final_answer: str
    faithfulness_score: float
    attempts_count: int
    success: bool
    model_name: str

class HealthResponse(BaseModel):
    status: str
    version: str
    vector_store: str
    redis_status: str
    llm_provider: str
    uptime_seconds: float