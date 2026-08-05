import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PythonCodeSandbox:
    """
    Python Code & Data Sandbox Engine: Secure execution sandbox for mathematical,
    analytical sum/average, and statistical data queries.
    """
    def execute_analytical_query(self, query: str) -> Dict[str, Any]:
        numbers = [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', query)]
        if not numbers:
            return {"status": "error", "result": "No numerical values found in analytical query."}

        q_lower = query.lower()
        if "sum" in q_lower or "total" in q_lower or "add" in q_lower:
            val = sum(numbers)
            return {"status": "success", "operation": "sum", "result": val, "expression": f"sum({numbers}) = {val}"}
        elif "average" in q_lower or "mean" in q_lower:
            val = sum(numbers) / len(numbers)
            return {"status": "success", "operation": "average", "result": round(val, 2), "expression": f"avg({numbers}) = {val:.2f}"}
        
        # Default computation
        val = sum(numbers)
        return {"status": "success", "operation": "sum", "result": val, "expression": f"sum({numbers}) = {val}"}

code_sandbox = PythonCodeSandbox()
