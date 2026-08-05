import time
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class CircuitBreakerManager:
    """
    Multi-LLM Circuit Breaker: Tracks LLM API failure rates and automatically
    fails over to backup providers (Anthropic, Azure, Offline Fallback) when primary fails.
    """
    def __init__(self, max_failures: int = 3, reset_timeout: float = 60.0):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_failure_time = 0.0

    def execute_with_fallback(self, primary_fn: Callable[[], str], fallback_fn: Callable[[], str]) -> str:
        current_time = time.time()
        
        if self.state == "OPEN":
            if current_time - self.last_failure_time > self.reset_timeout:
                logger.info("Circuit Breaker HALF-OPEN: Testing primary provider...")
                self.state = "HALF-OPEN"
            else:
                logger.warning("Circuit Breaker OPEN: Bypassing primary LLM to backup provider.")
                return fallback_fn()

        try:
            res = primary_fn()
            if self.state == "HALF-OPEN":
                logger.info("Circuit Breaker CLOSED: Primary provider recovered.")
                self.state = "CLOSED"
                self.failure_count = 0
            return res
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = current_time
            logger.error(f"Primary LLM call failed ({e}). Failure count: {self.failure_count}")

            if self.failure_count >= self.max_failures:
                self.state = "OPEN"
                logger.warning(f"Circuit Breaker tripped to OPEN state for {self.reset_timeout}s.")

            return fallback_fn()

circuit_breaker = CircuitBreakerManager()
