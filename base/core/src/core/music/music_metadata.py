import asyncio
import os
import uuid

from mutagen import File, FileType

from core.config import config
from core.db.models.music_info import MusicInfo
from core.logger.logger import logger
from core.utils.list_utils import get_first


async def load_from_dir() -> list[MusicInfo]:
    directory = config.get_env("MUSIC_FOLDER")
    tasks = []
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            audio = File(filepath)
            if audio is None:
                continue
            tasks.append(asyncio.create_task(parse_audio(audio, filepath)))
    return await asyncio.gather(*tasks, return_exceptions=True)


async def parse_audio(audio: FileType, filepath: str) -> MusicInfo:
    tag_mapping = config.music_tag_mapping()
    tags = audio.tags
    music_info = MusicInfo(
        uuid=str(uuid.uuid4()),
        filepath=os.path.normpath(filepath),
        album=get_first(tags[tag_mapping["album"]]),
        title=get_first(tags[tag_mapping["title"]]),
        artist=tags[tag_mapping["artist"]],
        date=get_first(tags[tag_mapping["date"]]),
        lyrics=get_first(tags[tag_mapping["lyrics"]]),
        album_artist=get_first(tags[tag_mapping["album_artist"]]),
        time_length=int(getattr(audio.info, "length", 0))
    )
    logger.info(f"loaded {music_info.title}-{','.join(music_info.artist)} in {music_info.filepath}")
    return music_info


if __name__ == '__main__':
    load_from_dir()
