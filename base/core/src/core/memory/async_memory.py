import uuid
from typing import Literal

from langgraph.checkpoint.redis import AsyncRedisSaver
from langgraph.store.redis import AsyncRedisStore
from pydantic import BaseModel

from core.client.redis import get_async_redis

_checkpointer: AsyncRedisSaver
_store: AsyncRedisStore


async def ainit_memory():
    global _checkpointer, _store
    async with AsyncRedisSaver(redis_client=get_async_redis()) as async_checkpointer:
        _checkpointer = async_checkpointer
        await _checkpointer.asetup()
    async with AsyncRedisStore(redis_client=get_async_redis()) as async_store:
        _store = async_store
        await _store.setup()


def get_checkpointer():
    global _checkpointer
    return _checkpointer


def get_store():
    global _store
    return _store


class MemoryItem(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str

    @classmethod
    def add_memories(cls, old_memories: list["MemoryItem"], new_memories: list["MemoryItem"]) -> list["MemoryItem"]:
        return old_memories or [] + new_memories or []


async def aput(memory_item: MemoryItem, *, namespace_prefix: str = "memories"):
    # FIXME 2025/11/8 xfdzcoder: 暂时没有用户这个维度，默认为 temp
    namespace = (namespace_prefix, "temp")
    await get_store().aput(namespace, str(uuid.uuid4()), memory_item.model_dump())


async def asearch(query: str, *, namespace_prefix: str = "memories") -> list[MemoryItem]:
    # FIXME 2025/11/8 xfdzcoder: 暂时没有用户这个维度，默认为 temp
    namespace = (namespace_prefix, "temp")
    memories = await get_store().asearch(namespace, query=query)
    return [memory.value for memory in memories]
