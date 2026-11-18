import json
import logging
import redis
from config import Config

logger = logging.getLogger(__name__)

# Initialize Redis client with fast timeout and fallback to FakeRedis
redis_client = None
_using_fake = False

try:
    client = redis.Redis.from_url(
        Config.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=0.1,
        socket_timeout=0.1
    )
    client.ping()
    redis_client = client
    logger.info("Connected to Redis server successfully.")
except Exception as e:
    try:
        import fakeredis
        redis_client = fakeredis.FakeRedis(decode_responses=True)
        _using_fake = True
        logger.info("Redis server not available; fallback to instant FakeRedis cache.")
    except Exception:
        redis_client = None

def get_cache(key):
    """Retrieve cached data from Redis or fallback cache."""
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
    return None

def set_cache(key, value, timeout_seconds=300):
    """Store data in cache with expiry."""
    if not redis_client:
        return
    try:
        redis_client.set(key, json.dumps(value), ex=timeout_seconds)
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")

def invalidate_treks_cache():
    """Clear cached trek data upon updates."""
    if not redis_client:
        return
    try:
        keys = redis_client.keys("treks:*")
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        logger.warning(f"Cache clear failed: {e}")

