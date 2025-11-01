import os
from pathlib import Path

from dotenv import load_dotenv

from base.core.src.logger.logger import logger


def load_config():
    loaded = load_dotenv(Path(__file__).parent / f".env.{os.getenv('APP_ENV')}")
    if not loaded:
        raise RuntimeError(".env.dev not found")
    logger.info("env loaded")


if __name__ == '__main__':
    load_config()
