import logging
from fastapi import APIRouter
from fastapi.responses import Response
from app.utils.metrics import metrics

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/audit/logs")
async def get_audit_logs():
    return {"total_logs": len(metrics.audit_logs), "logs": metrics.audit_logs}

@router.get("/audit/export")
async def export_audit_csv():
    csv_data = metrics.generate_audit_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rag_evaluation_audit_report.csv"}
    )
