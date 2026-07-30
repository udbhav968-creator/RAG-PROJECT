import json
import logging
import time
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback in-memory store
_memory_cache: Dict[str, Dict[str, Any]] = {}

def _get_redis_sync():
    try:
        import redis
        return redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1.0)
    except Exception as e:
        logger.debug(f"Redis connection unavailable: {e}")
        return None

async def get_cached_answer(question: str) -> Optional[dict]:
    return get_cached_answer_sync(question)

async def set_cached_answer(question: str, data: dict, ttl: int = settings.CACHE_TTL):
    set_cached_answer_sync(question, data, ttl)

def get_cached_answer_sync(question: str) -> Optional[dict]:
    key = f"answer:{question}"
    # Try Redis first
    r = _get_redis_sync()
    if r:
        try:
            cached = r.get(key)
            if cached:
                logger.info(f"Cache HIT (Redis) for query: '{question}'")
                return json.loads(cached)
        except Exception as e:
            logger.debug(f"Redis get failed: {e}")

    # Fallback to memory cache
    if key in _memory_cache:
        item = _memory_cache[key]
        if item["expires_at"] > time.time():
            logger.info(f"Cache HIT (Memory) for query: '{question}'")
            return item["data"]
        else:
            del _memory_cache[key]
            
    logger.info(f"Cache MISS for query: '{question}'")
    return None

def set_cached_answer_sync(question: str, data: dict, ttl: int = settings.CACHE_TTL):
    key = f"answer:{question}"
    # Try Redis
    r = _get_redis_sync()
    if r:
        try:
            r.set(key, json.dumps(data), ex=ttl)
        except Exception as e:
            logger.debug(f"Redis set failed: {e}")

    # Store in memory fallback
    _memory_cache[key] = {
        "data": data,
        "expires_at": time.time() + ttl
    }