import redis
from app.core.config import settings

# decode_responses=True ensures we get strings/ints back instead of bytes
redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)


def get_failed_attempts(key: str) -> int:
    value = redis_client.get(key)
    return int(value) if value else 0


def increment_failed_login(key: str, ttl: int = 600):
    # Increment the value (creates key at 0 then sets to 1 if it didn't exist)
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, ttl)
    return count
