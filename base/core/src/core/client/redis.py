from redis.asyncio import Redis as AsyncRedis

from core.config import config

_async_redis_client: AsyncRedis


async def ainit_redis():
    global _async_redis_client
    _async_redis_client = AsyncRedis(
        host=config.get_env("REDIS_HOST"),
        port=config.get_env("REDIS_PORT"),
        username=config.get_env("REDIS_USERNAME"),
        password=config.get_env("REDIS_PASSWORD"),
        db=config.get_env("REDIS_DB")
    )


def get_async_redis() -> AsyncRedis:
    global _async_redis_client
    return _async_redis_client
