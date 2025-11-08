import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

from core.logger.logger import logger

_ENVS = Literal[
    "APP_ENV",
    "DEEPSEEK_API_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_BASE_URL",
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_USERNAME",
    "REDIS_PASSWORD",
    "REDIS_DB",
]
_default : dict[_ENVS, str] = {
    "APP_ENV": "dev",
    "DEEPSEEK_API_KEY": "",
    "LANGFUSE_SECRET_KEY": "",
    "LANGFUSE_PUBLIC_KEY": "",
    "LANGFUSE_BASE_URL": "",
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PORT": "6379",
    "REDIS_USERNAME": "",
    "REDIS_PASSWORD": "",
    "REDIS_DB": "0",
}



def load_config():
    env_path = Path(__file__).parent / f".env.{os.getenv('APP_ENV', default='dev')}"
    loaded = load_dotenv(env_path)
    if not loaded:
        raise RuntimeError(".env.dev not found")
    logger.info("env loaded")


def _get_default(key: _ENVS):
    return _default[key]


def get_env(key: _ENVS, *, default=None):
    val = os.getenv(key, default)
    if val is not None:
        return val
    return _get_default(key)


if __name__ == '__main__':
    load_config()
