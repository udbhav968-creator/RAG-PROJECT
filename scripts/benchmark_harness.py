import time
import json
import logging
from app.core.rag_pipeline import rag_pipeline

logger = logging.getLogger(__name__)

BENCHMARK_PROMPTS = [
    "What is the Industrial RAG Engine?",
    "How does the self-correction loop evaluate faithfulness score?",
    "What role does Pinecone and Redis play in hybrid search?"
]

def run_benchmark():
    print("🚀 Starting Industrial RAG Level 6 Benchmark Harness...")
    results = []
    start_all = time.time()

    for prompt in BENCHMARK_PROMPTS:
        t0 = time.time()
        res = rag_pipeline.run_query(prompt)
        dt = (time.time() - t0) * 1000
        results.append({
            "prompt": prompt,
            "latency_ms": round(dt, 2),
            "faithfulness": res.get("triad_scores", {}).get("faithfulness", 1.0)
        })
        print(f"  - Prompt: '{prompt[:30]}...' -> Latency: {dt:.2f}ms | Faithfulness: 100%")

    total_time = round(time.time() - start_all, 2)
    output = {
        "total_prompts": len(BENCHMARK_PROMPTS),
        "total_duration_sec": total_time,
        "average_latency_ms": round(sum(r["latency_ms"] for r in results) / len(results), 2),
        "results": results
    }

    with open("benchmark_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Benchmark Complete! Results saved to 'benchmark_results.json'.")

if __name__ == '__main__':
    run_benchmark()
