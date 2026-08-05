"""
Industrial RAG Triad Metrics Benchmark Suite
Evaluates Faithfulness, Answer Relevance, Context Precision, and Context Recall across benchmark queries.
"""
import time
import json
from app.core.rag_pipeline import rag_pipeline
from app.core.evaluator import triad_evaluator

def run_triad_benchmark():
    print("🏆 Starting RAG Triad Evaluation Benchmark...")
    test_queries = [
        "What is the Industrial RAG Engine and how does it work?",
        "How does the self-correction loop evaluate faithfulness score?",
        "What roles do Celery, Redis, and Pinecone play in the pipeline?"
    ]
    
    start_time = time.time()
    benchmark_data = []

    for q in test_queries:
        res = rag_pipeline.run_query(q, max_attempts=2)
        triad = res.get("triad_scores", {})
        benchmark_data.append({
            "question": q,
            "selected_tool": res.get("selected_tool", "hybrid_vector_search"),
            "triad_scores": triad,
            "final_answer": res.get("final_answer", "")[:120] + "..."
        })
        print(f"\n  [✓] Query: '{q[:35]}...'")
        print(f"      Selected Tool: {res.get('selected_tool')}")
        print(f"      Faithfulness: {triad.get('faithfulness')} | Relevance: {triad.get('answer_relevance')} | Precision: {triad.get('context_precision')} | Recall: {triad.get('context_recall')}")
        print(f"      Triad Average: {triad.get('triad_average')}")

    total_time = round(time.time() - start_time, 2)
    avg_triad = round(sum(d["triad_scores"].get("triad_average", 0) for d in benchmark_data) / len(benchmark_data), 3)
    
    print(f"\n✨ Benchmark Finished in {total_time}s! Average RAG Triad Score: {avg_triad}")
    return {"total_time": total_time, "average_triad_score": avg_triad, "details": benchmark_data}

if __name__ == "__main__":
    run_triad_benchmark()
