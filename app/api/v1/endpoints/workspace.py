import logging
from fastapi import APIRouter
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

WORKSPACES_STORE: Dict[str, Dict[str, Any]] = {
    "ws_default": {"workspace_id": "ws_default", "name": "Global Research Workspace", "members": 5}
}

@router.get("/workspace/list")
async def list_workspaces():
    return {"workspaces": list(WORKSPACES_STORE.values())}
