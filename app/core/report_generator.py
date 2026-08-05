import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ExecutiveReportGenerator:
    """
    Executive Report Generator: Compiles HTML audit reports containing query answers,
    source citations, and RAG Triad evaluation metrics.
    """
    def generate_html_report(self, query_result: Dict[str, Any]) -> str:
        question = query_result.get("question", "N/A")
        answer = query_result.get("final_answer", "N/A")
        triad = query_result.get("triad_scores", {})
        citations = query_result.get("citations", [])

        cit_html = "".join([f"<li><b>[{c.get('document_id')}, Chunk #{c.get('chunk_index')}]</b>: {c.get('text_snippet')}</li>" for c in citations])

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <title>Industrial RAG Executive Audit Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; }}
    .card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; margin-bottom: 20px; }}
    .score {{ font-weight: bold; color: #34d399; }}
    h1 {{ color: #818cf8; }}
  </style>
</head>
<body>
  <h1>📊 Industrial RAG Executive Audit Report</h1>
  <div class="card">
    <h2>Prompt Question</h2>
    <p>"{question}"</p>
  </div>
  <div class="card">
    <h2>Grounded AI Answer</h2>
    <p>{answer}</p>
  </div>
  <div class="card">
    <h2>RAG Triad Evaluation Scores</h2>
    <p>Faithfulness: <span class="score">{triad.get('faithfulness', 1.0) * 100}%</span></p>
    <p>Answer Relevance: <span class="score">{triad.get('answer_relevance', 1.0) * 100}%</span></p>
    <p>Context Precision: <span class="score">{triad.get('context_precision', 1.0) * 100}%</span></p>
    <p>Context Recall: <span class="score">{triad.get('context_recall', 1.0) * 100}%</span></p>
  </div>
  <div class="card">
    <h2>Grounded Citations</h2>
    <ul>{cit_html or '<li>No explicit citations</li>'}</ul>
  </div>
</body>
</html>"""
        return html_content

report_generator = ExecutiveReportGenerator()
