import uuid
from typing import Literal
from urllib.parse import quote_plus

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

from core.config import config
from core.context.context import ContextHolder

_checkpointer: PostgresSaver | None = None
_store: PostgresStore | None = None
_pool: ConnectionPool | None = None


def init_memory():
    global _checkpointer, _store, _pool
    user = config.get_env("POSTGRES_USER")
    password = config.get_env("POSTGRES_PASSWORD")
    host = config.get_env("POSTGRES_HOST")
    port = config.get_env("POSTGRES_PORT")
    db = config.get_env("POSTGRES_DB")

    _pool = ConnectionPool(conninfo=f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/{db}?sslmode=disable")
    _checkpointer = PostgresSaver(conn=_pool) # noqa
    _checkpointer.setup()
    _store = PostgresStore(conn=_pool) # noqa
    _store.setup()


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


def put(memory_item: MemoryItem, *, namespace_prefix: str = "memories"):
    namespace = (namespace_prefix, ContextHolder.user_id())
    get_store().put(namespace, str(uuid.uuid4()), memory_item.model_dump())


def search(query: str, *, namespace_prefix: str = "memories") -> list[MemoryItem]:
    namespace = (namespace_prefix, ContextHolder.user_id())
    memories = get_store().search(namespace, query=query)
    return [memory.value for memory in memories]
