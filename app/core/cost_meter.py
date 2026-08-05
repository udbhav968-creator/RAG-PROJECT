import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Model Cost per 1,000 Tokens (USD)
MODEL_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "local": {"input": 0.0, "output": 0.0}
}

class TokenCostMeter:
    """
    Real-Time Token & Cost Metering Engine: Tracks prompt/completion token counts
    and calculates live API cost per request.
    """
    def calculate_cost(self, prompt_text: str, completion_text: str, model_name: str = "gpt-4") -> Dict[str, Any]:
        prompt_tokens = len(prompt_text.split())
        completion_tokens = len(completion_text.split())
        total_tokens = prompt_tokens + completion_tokens

        pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["local"])
        input_cost = (prompt_tokens / 1000.0) * pricing["input"]
        output_cost = (completion_tokens / 1000.0) * pricing["output"]
        total_cost_usd = round(input_cost + output_cost, 6)

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": total_cost_usd,
            "model_name": model_name
        }

cost_meter = TokenCostMeter()
