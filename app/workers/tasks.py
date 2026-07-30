import logging
from app.workers.celery_app import celery_app
from app.core.rag_pipeline import rag_pipeline

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=2)
def process_query(self, question: str, max_attempts: int = None):
    try:
        logger.info(f"Processing query via Celery task: '{question}'")
        return rag_pipeline.run_query(question, max_attempts=max_attempts)
    except Exception as exc:
        logger.error(f"Error in process_query task: {exc}")
        raise self.retry(exc=exc, countdown=2)

@celery_app.task(bind=True, max_retries=2)
def ingest_document(self, doc_id: str, content: str, chunk_size: int = 500, chunk_overlap: int = 50):
    try:
        logger.info(f"Ingesting document via Celery task: '{doc_id}'")
        return rag_pipeline.ingest_document_text(
            document_id=doc_id,
            content=content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    except Exception as exc:
        logger.error(f"Error in ingest_document task: {exc}")
        raise self.retry(exc=exc, countdown=2)