import time
import uuid
import csv
import io
from typing import Dict, Any, List

class SystemMetrics:
    def __init__(self):
        self.total_queries = 0
        self.total_ingested_docs = 0
        self.total_ingested_chunks = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.faithfulness_scores = []
        self.attempts_history = []
        self.audit_logs: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def record_query(self, question: str, final_answer: str, success: bool, faithfulness_score: float, attempts_count: int, from_cache: bool = False, model_name: str = "gpt-4") -> str:
        self.total_queries += 1
        if from_cache:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        if faithfulness_score is not None:
            self.faithfulness_scores.append(faithfulness_score)
        self.attempts_history.append(attempts_count)

        audit_id = f"AUDIT-{uuid.uuid4().hex[:8].upper()}"
        log_entry = {
            "audit_id": audit_id,
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "question": question,
            "final_answer": final_answer,
            "faithfulness_score": round(faithfulness_score or 0.0, 3),
            "attempts_count": attempts_count,
            "success": success,
            "from_cache": from_cache,
            "model_name": model_name
        }
        self.audit_logs.append(log_entry)
        return audit_id

    def record_ingestion(self, doc_id: str, chunk_count: int):
        self.total_ingested_docs += 1
        self.total_ingested_chunks += chunk_count

    def get_summary(self) -> Dict[str, Any]:
        avg_faithfulness = (
            sum(self.faithfulness_scores) / len(self.faithfulness_scores)
            if self.faithfulness_scores else 0.0
        )
        avg_attempts = (
            sum(self.attempts_history) / len(self.attempts_history)
            if self.attempts_history else 0.0
        )
        total_cache = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache * 100) if total_cache > 0 else 0.0

        return {
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "average_faithfulness_score": round(avg_faithfulness, 3),
            "average_correction_attempts": round(avg_attempts, 2),
            "total_ingested_docs": self.total_ingested_docs,
            "total_ingested_chunks": self.total_ingested_chunks,
            "audit_logs_recorded": len(self.audit_logs)
        }

    def generate_audit_csv(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Audit ID", "Timestamp", "Question", "Final Answer", "Faithfulness Score", "Attempts Count", "Passed Evaluation", "Cached", "Model Name"])
        
        for entry in self.audit_logs:
            writer.writerow([
                entry["audit_id"],
                entry["formatted_time"],
                entry["question"],
                entry["final_answer"],
                entry["faithfulness_score"],
                entry["attempts_count"],
                entry["success"],
                entry["from_cache"],
                entry["model_name"]
            ])
        return output.getvalue()

metrics = SystemMetrics()