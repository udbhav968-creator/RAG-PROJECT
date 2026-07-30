import logging
from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse
from app.core.rag_pipeline import rag_pipeline
from app.workers.tasks import process_query

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        # Try Celery async delegation first
        try:
            task = process_query.delay(request.question, request.max_attempts)
            result = task.get(timeout=15)
            return QueryResponse(**result)
        except Exception as celery_err:
            logger.info(f"Celery task delegation unavailable ({celery_err}). Running RAGPipeline inline.")
            result = rag_pipeline.run_query(
                request.question,
                max_attempts=request.max_attempts,
                model_name=request.model_name
            )
            return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))