"""
Synthetic Evaluation Benchmark Generator
Generates synthetic Question-Context-Answer test triples from ingested knowledge base documents.
"""
import time
import json
from app.core.rag_pipeline import rag_pipeline
from app.core.evaluator import triad_evaluator

def generate_synthetic_benchmark():
    print("🧪 Generating Synthetic Evaluation Test Suite...")
    
    sample_doc = "Hydraulic pressure sensor PS-101 monitors main line pressure up to 500 bar with +/- 0.5% accuracy."
    rag_pipeline.ingest_document_text("SYNTHETIC_SPEC_001", sample_doc)

    synthetic_prompts = [
        "What pressure limit does PS-101 monitor?",
        "What is the accuracy of PS-101 hydraulic sensor?"
    ]

    results = []
    for q in synthetic_prompts:
        res = rag_pipeline.run_query(q)
        results.append({
            "synthetic_question": q,
            "answer": res.get("final_answer"),
            "triad_scores": res.get("triad_scores")
        })
        print(f"  [✓] Question: '{q}' -> Faithfulness: {res.get('triad_scores', {}).get('faithfulness')}")

    print(f"\n✨ Generated {len(results)} Synthetic Evaluation Cases Successfully!")
    return results

if __name__ == "__main__":
    generate_synthetic_benchmark()
