import logging
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core.rag_pipeline import rag_pipeline
from app.core.report_generator import report_generator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/report/html", response_class=HTMLResponse)
async def get_html_report(query: str = "What is Industrial RAG Engine?"):
    result = rag_pipeline.run_query(query)
    html_content = report_generator.generate_html_report(result)
    return HTMLResponse(content=html_content)
