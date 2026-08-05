import json
import logging
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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

@router.post("/query/stream")
async def stream_query_endpoint(request: QueryRequest):
    async def sse_generator():
        # Execute RAG Pipeline query
        result = rag_pipeline.run_query(
            request.question,
            max_attempts=request.max_attempts,
            model_name=request.model_name
        )

        # Stream status event
        yield f"data: {json.dumps({'event': 'status', 'message': 'Retrieved knowledge & evaluated faithfulness', 'selected_tool': result.get('selected_tool')})}\n\n"
        await asyncio.sleep(0.05)

        # Stream answer tokens word by word
        answer_text = result["final_answer"]
        tokens = answer_text.split()
        for token in tokens:
            chunk_data = json.dumps({"event": "token", "token": token + " "})
            yield f"data: {chunk_data}\n\n"
            await asyncio.sleep(0.03)

        # Stream completion event with full metadata & RAG Triad scores
        yield f"data: {json.dumps({'event': 'done', 'result': result})}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")