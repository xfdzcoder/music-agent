from _datetime import datetime
from typing import Any, ClassVar, Awaitable, Coroutine

from chat.repository import BaseRedisModel
from core.client.redis import get_async_redis
from core.context.context import ContextHolder


class UserThreadInfo(BaseRedisModel):
    _key_format: ClassVar[str] = "user_thread:{user_id}"

    user_id: str
    thread_id: str
    name: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @classmethod
    def format_key(cls, user_id: str):
        return cls._key_format.format(user_id=user_id)


async def list_thread() -> list[UserThreadInfo]:
    json_str_list: list[str] = await get_async_redis().lrange(UserThreadInfo.format_key(ContextHolder.user_id()), 0, -1)
    return [UserThreadInfo.model_validate_json(json_str) for json_str in json_str_list]


async def add_or_update_thread(thread_id: str, name: str = "Chat"):
    redis_key = UserThreadInfo.format_key(ContextHolder.user_id())
    thread_list = await list_thread()
    existed_thread_id_list = [thread.thread_id for thread in thread_list]
    if thread_id in existed_thread_id_list:
        existed_index = existed_thread_id_list.index(thread_id)
        existed_thread = thread_list[existed_index]
        existed_thread.updated_at = datetime.now()
        await get_async_redis().lset(redis_key, existed_index, existed_thread.model_dump_json())
    else:
        thread = UserThreadInfo(user_id=ContextHolder.user_id(), thread_id=thread_id, name=name)
        await get_async_redis().lpush(redis_key, thread.model_dump_json())
