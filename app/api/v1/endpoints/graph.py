import logging
from fastapi import APIRouter
from app.core.graph_rag import graph_engine

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/graph/data")
async def get_graph_data():
    """
    Returns node-link JSON structure for rendering the interactive Knowledge Graph canvas.
    """
    nodes_list = [
        {"id": node_id, "label": node_id, "group": data.get("type", "Entity")}
        for node_id, data in graph_engine.nodes.items()
    ]
    edges_list = [
        {"source": edge["source"], "target": edge["target"], "label": edge["relation"]}
        for edge in graph_engine.edges
    ]
    return {
        "nodes": nodes_list,
        "links": edges_list,
        "summary": graph_engine.get_graph_summary()
    }
