import asyncio

from langgraph.checkpoint.redis import RedisSaver, AsyncRedisSaver
from langgraph.store.redis import RedisStore, AsyncRedisStore
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from core.config import config

redis_client = Redis(
    host=config.get_env("REDIS_HOST"),
    port=config.get_env("REDIS_PORT"),
    username=config.get_env("REDIS_USERNAME"),
    password=config.get_env("REDIS_PASSWORD"),
    db=config.get_env("REDIS_DB")
)

checkpointer = RedisSaver(redis_client=redis_client)
store = RedisStore(conn=redis_client)

async_redis_client : AsyncRedis
async_checkpointer : AsyncRedisSaver
async_store : AsyncRedisStore

async def init_memory():
    global async_redis_client, async_checkpointer, async_store
    async_redis_client = AsyncRedis(
        host=config.get_env("REDIS_HOST"),
        port=config.get_env("REDIS_PORT"),
        username=config.get_env("REDIS_USERNAME"),
        password=config.get_env("REDIS_PASSWORD"),
        db=config.get_env("REDIS_DB")
    )
    async with AsyncRedisSaver(redis_client=async_redis_client) as async_checkpointer:
        async_checkpointer = async_checkpointer
    async with AsyncRedisStore(redis_client=async_redis_client) as async_store:
        async_store = async_store