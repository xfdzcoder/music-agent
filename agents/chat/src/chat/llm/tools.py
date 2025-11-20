from langchain_core.tools import tool

from core.db.models.music_info import search_music
from core.logger.logger import logger
from core.music.model import MusicInfo

@tool
def search_music_info_by_title(keyword: str) -> list[MusicInfo]:
    """
    Search for music information by title.

    :param keyword: The title or part of the title to be searched should contain only the title itself,
                    without any other explanatory content, to avoid affecting the search
    :return: A list of MusicInfo objects that match the given title.
    """
    logger.info(f"Search for music information by title: {keyword}")
    res = search_music(keyword)
    logger.info(f"Search result: {res}")
    return [MusicInfo.model_validate(music_info) for music_info in res]
