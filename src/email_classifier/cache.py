import redis
from .config import REDIS_URL
from typing import Optional

redis_client = redis.StrictRedis.from_url(
    REDIS_URL, socket_timeout=5, decode_responses=True
)

def get_cache(key: str) -> Optional[str]:
    try:
        return redis_client.get(key)
    except Exception:
        return None

def set_cache(key: str, value: str, ex=None) -> None:
    try:
        redis_client.setex(key, ex, value)
    except Exception:
        pass 