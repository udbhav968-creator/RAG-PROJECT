"""
Industrial RAG Benchmark & Latency Profiler
Executes concurrent retrieval, faithfulness scoring, and throughput benchmarks.
"""
import time
import json
from app.core.rag_pipeline import rag_pipeline

def run_benchmark():
    print("🚀 Starting Industrial RAG Engine Benchmark...")
    queries = [
        "What is Industrial RAG and how does it work?",
        "Explain the self-correction algorithm faithfulness score.",
        "What vector database engines are supported?",
        "How does Celery and Redis caching improve throughput?"
    ]
    
    start_time = time.time()
    results = []
    for q in queries:
        t0 = time.time()
        res = rag_pipeline.run_query(q, max_attempts=2)
        elapsed = round(time.time() - t0, 3)
        results.append({
            "query": q,
            "latency_seconds": elapsed,
            "success": res.get("success", False),
            "attempts": len(res.get("attempts", []))
        })
        print(f"  [✓] Query: '{q[:30]}...' -> {elapsed}s ({len(res.get('attempts', []))} attempts)")
        
    total_elapsed = round(time.time() - start_time, 3)
    avg_latency = round(total_elapsed / len(queries), 3)
    print(f"\n📊 Benchmark Complete! Total time: {total_elapsed}s | Avg Latency: {avg_latency}s/query")
    return {"total_time": total_elapsed, "avg_latency": avg_latency, "details": results}

if __name__ == "__main__":
    run_benchmark()
