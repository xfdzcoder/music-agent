import os
from pathlib import Path

from dotenv import load_dotenv

from core.logger.logger import logger


def load_config():
    env_path = Path(__file__).parent / f".env.{os.getenv('APP_ENV', default='dev')}"
    loaded = load_dotenv(env_path)
    if not loaded:
        raise RuntimeError(".env.dev not found")
    logger.info("env loaded")


if __name__ == '__main__':
    load_config()
