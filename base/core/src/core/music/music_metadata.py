import asyncio
import os
import uuid
from asyncio import Task

from mutagen import File, FileType

from core.config import config
from core.db.models.music_info import MusicInfo
from core.logger.logger import logger
from core.utils.list_utils import get_first


class TaskException(Exception):
    def __init__(self, cause: Exception, filepath: str, audio: FileType):
        super().__init__(str(cause))
        self.cause = cause
        self.filepath = filepath
        self.audio = audio


async def load_from_dir() -> list[MusicInfo]:
    directory = config.get_env("MUSIC_FOLDER")
    tasks : list[Task] = []
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            audio = File(filepath)
            if audio is None:
                logger.warning(f"{filepath} is not a music file")
                continue
            logger.info(f"parsing {filepath}")
            tasks.append(asyncio.create_task(parse_audio(audio, filepath)))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    succeeds : list[MusicInfo] = []
    for task, result in zip(tasks, results):
        if isinstance(result, TaskException):
            logger.warning(
                f"parse error: {result.filepath}\t"
                f"{result.audio.tags}"
            )
        if isinstance(result, MusicInfo):
            succeeds.append(result)
    return succeeds


async def parse_audio(audio: FileType, filepath: str) -> MusicInfo:
    try:
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
    except Exception as e:
        raise TaskException(e, filepath, audio)


if __name__ == '__main__':
    load_from_dir()
