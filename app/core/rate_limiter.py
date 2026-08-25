import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TokenBucketRateLimiter:
    """
    Token Bucket Rate Limiter & DDoS Shield:
    Limits API request frequency per client IP to prevent API exhaustion.
    """
    def __init__(self, capacity: int = 100, fill_rate: float = 10.0):
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.tokens: Dict[str, float] = {}
        self.last_update: Dict[str, float] = {}

    def allow_request(self, client_ip: str) -> bool:
        now = time.time()
        if client_ip not in self.tokens:
            self.tokens[client_ip] = float(self.capacity)
            self.last_update[client_ip] = now

        delta = now - self.last_update[client_ip]
        self.tokens[client_ip] = min(float(self.capacity), self.tokens[client_ip] + delta * self.fill_rate)
        self.last_update[client_ip] = now

        if self.tokens[client_ip] >= 1.0:
            self.tokens[client_ip] -= 1.0
            return True
        else:
            logger.warning(f"Rate Limiter blocked request from client IP: '{client_ip}'")
            return False

rate_limiter = TokenBucketRateLimiter()
