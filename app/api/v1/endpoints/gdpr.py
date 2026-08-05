import logging
from fastapi import APIRouter
from app.core.gdpr import gdpr_engine

logger = logging.getLogger(__name__)
router = APIRouter()

@router.delete("/gdpr/purge/{doc_id}")
async def purge_doc_data(doc_id: str):
    return gdpr_engine.purge_document_data(doc_id)
