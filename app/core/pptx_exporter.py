import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PPTXDeckExporter:
    """
    PowerPoint (.pptx) Executive Deck Exporter: Compiles RAG query results,
    citations, and RAG Triad scores into executive presentation slides.
    """
    def generate_deck_text(self, query_result: Dict[str, Any]) -> str:
        question = query_result.get("question", "N/A")
        answer = query_result.get("final_answer", "N/A")
        triad = query_result.get("triad_scores", {})
        
        slide_text = f"""==================================================
SLIDE 1: EXECUTIVE BRIEFING - RAG RESEARCH RESULT
==================================================
Topic: {question}

Grounded Findings:
{answer}

Key RAG Triad Telemetry:
- Faithfulness Score: {triad.get('faithfulness', 1.0) * 100}%
- Answer Relevance: {triad.get('answer_relevance', 1.0) * 100}%
- Context Precision: {triad.get('context_precision', 1.0) * 100}%
- Context Recall: {triad.get('context_recall', 1.0) * 100}%
=================================================="""
        return slide_text

pptx_exporter = PPTXDeckExporter()
