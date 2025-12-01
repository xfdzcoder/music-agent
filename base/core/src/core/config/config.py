import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

from core.logger.logger import logger

_ENVS = Literal[
    "APP_ENV",
    "BASE_URL",
    "DEEPSEEK_API_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_BASE_URL",

    "MUSIC_FOLDER",
    "MUSIC_TAG_MAPPING",

    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",

    "MI_USERNAME",
    "MI_PASSWORD",

    "LRC_API_BASE_URL",
    "LRC_API_KEY",
]
_default: dict[_ENVS, str] = {
    "APP_ENV": "dev",
    "BASE_URL": "",
    "DEEPSEEK_API_KEY": "",
    "LANGFUSE_SECRET_KEY": "",
    "LANGFUSE_PUBLIC_KEY": "",
    "LANGFUSE_BASE_URL": "",

    "MUSIC_FOLDER": "",
    "MUSIC_TAG_MAPPING": "album=album,title=title,artist=artist,date=date,lyrics=lyrics,album_artist=albumartist",

    "POSTGRES_USER": "",
    "POSTGRES_PASSWORD": "",
    "POSTGRES_HOST": "",
    "POSTGRES_PORT": "",
    "POSTGRES_DB": "",

    "MI_USERNAME": "",
    "MI_PASSWORD": "",

    "LRC_API_BASE_URL": "http://127.0.0.1:28883",
    "LRC_API_KEY": "",
}


def load_config():
    env_path = Path(__file__).parent / f".env.{os.getenv('APP_ENV', default='dev')}"
    loaded = load_dotenv(env_path)
    if not loaded:
        raise RuntimeError(".env.dev not found")
    logger.info("env loaded")


def _get_default(key: _ENVS):
    return _default[key]


def get_env(key: _ENVS, *, default=None) -> str:
    val = os.getenv(key, default)
    if val:
        return val
    return _get_default(key)


_music_tag_mapping: dict[str, str] | None = None


def music_tag_mapping() -> dict[str, str]:
    global _music_tag_mapping
    if _music_tag_mapping:
        return _music_tag_mapping
    mapping_str = get_env("MUSIC_TAG_MAPPING")
    _music_tag_mapping = dict()
    for kv in mapping_str.split(","):
        kv_split = kv.split("=")
        _music_tag_mapping[kv_split[0]] = kv_split[1]
    return _music_tag_mapping


if __name__ == '__main__':
    load_config()
