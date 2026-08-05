import logging
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.core.rag_pipeline import rag_pipeline
from app.core.pptx_exporter import pptx_exporter

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/export/deck", response_class=PlainTextResponse)
async def export_pptx_deck(query: str = "What is Industrial RAG Engine?"):
    result = rag_pipeline.run_query(query)
    deck_text = pptx_exporter.generate_deck_text(result)
    return PlainTextResponse(content=deck_text)
