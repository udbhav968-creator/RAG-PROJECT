from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = ""
    MODEL_NAME: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    PINECONE_API_KEY: Optional[str] = ""
    PINECONE_ENVIRONMENT: Optional[str] = "us-east-1"
    PINECONE_INDEX_NAME: Optional[str] = "industrial-rag"
    VECTOR_STORE_TYPE: str = "auto"  # 'pinecone', 'memory', or 'auto'
    
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    FAITHFULNESS_THRESHOLD: float = 0.7
    MAX_CORRECTION_ATTEMPTS: int = 2
    TOP_K_RETRIEVAL: int = 5
    CACHE_TTL: int = 3600
    
    ALLOW_ORIGINS: List[str] = ["*"]
    ENABLE_MOCK_FALLBACK: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()