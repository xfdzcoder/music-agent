import uuid

from langgraph.checkpoint.redis import AsyncRedisSaver
from langgraph.store.redis import AsyncRedisStore
from pydantic import BaseModel
from redis.asyncio import Redis as AsyncRedis

from core.config import config

redis_client: AsyncRedis
checkpointer: AsyncRedisSaver
store: AsyncRedisStore


async def ainit_memory():
    global redis_client, checkpointer, store
    async_redis_client = AsyncRedis(
        host=config.get_env("REDIS_HOST"),
        port=config.get_env("REDIS_PORT"),
        username=config.get_env("REDIS_USERNAME"),
        password=config.get_env("REDIS_PASSWORD"),
        db=config.get_env("REDIS_DB")
    )
    async with AsyncRedisSaver(redis_client=async_redis_client) as async_checkpointer:
        checkpointer = async_checkpointer
        await checkpointer.asetup()
    async with AsyncRedisStore(redis_client=async_redis_client) as async_store:
        store = async_store
        await store.setup()


class MemoryItem(BaseModel):
    content: str


async def put_memory(memory_item: MemoryItem, *, namespace_prefix: str = "memories"):
    # FIXME 2025/11/8 xfdzcoder: 暂时没有用户这个维度，默认为 temp
    namespace = (namespace_prefix, "temp")
    await store.aput(namespace, str(uuid.uuid4()), memory_item.model_dump())
