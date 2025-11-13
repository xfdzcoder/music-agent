import json

from redis.commands.search.query import Query
from redisvl.index import AsyncSearchIndex

from core.client.redis import get_async_redis
from core.music.model import MusicInfo

_REDIS_KEY_SEPARATOR = ":"
_MUSIC_PREFIX = "music"

_SCHEMA = {
    "index": {
        "name": "idx_music",
        "prefix": _MUSIC_PREFIX + _REDIS_KEY_SEPARATOR,
        "storage_type": "json",
    },
    "fields": [
        {"name": "uuid", "type": "tag"},
        {"name": "album", "type": "text"},
        {"name": "title", "type": "text"},
        {"name": "artist", "type": "tag"},
        {"name": "date", "type": "numeric"},
        {"name": "lyrics", "type": "text"},
        {"name": "album_artist", "type": "text"},
        {"name": "time_length", "type": "numeric"},
    ],
}


async def set_json(music_info: MusicInfo):
    async_redis = get_async_redis()
    await async_redis.json().set(
        _MUSIC_PREFIX + _REDIS_KEY_SEPARATOR + music_info.uuid,
        "$",
        music_info.model_dump()
    )


_music_index: AsyncSearchIndex


async def create_index():
    global _music_index
    async_redis = get_async_redis()

    _music_index = AsyncSearchIndex.from_dict(
        _SCHEMA, redis_client=async_redis
    )
    await _music_index.create(overwrite=True)


async def search_music(query: Query) -> list[MusicInfo]:
    result = await _music_index.search(query)
    if result.total == 0:
        return []
    return [json.loads(doc.json) for doc in result.docs]


async def list_music():
    async_redis = get_async_redis()
    return await async_redis.keys(_MUSIC_PREFIX + _REDIS_KEY_SEPARATOR + "*")


async def clear_music(keys: list[str]):
    async_redis = get_async_redis()
    await async_redis.delete(*keys)
