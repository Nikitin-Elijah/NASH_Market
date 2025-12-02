import redis.asyncio as redis
import pickle
import functools

from src.config import REDIS_URL

REDIS = redis.from_url(REDIS_URL)


def redis_cache(prefix: str, ttl: int = 60):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{func.__qualname__}:{kwargs}"
            cached = await REDIS.get(key)
            if cached:
                return pickle.loads(cached)
            result = await func(*args, **kwargs)
            await REDIS.set(key, pickle.dumps(result), ex=ttl)
            return result

        return wrapper

    return decorator


async def cache_delete_prefix(prefix: str):
    print(f'Пора удалять по префиксу: {prefix}')
    keys = await REDIS.keys(pattern=f'{prefix}:*')
    print(f'-------------------------------> {keys}')
    if keys:
        await REDIS.delete(*keys)
