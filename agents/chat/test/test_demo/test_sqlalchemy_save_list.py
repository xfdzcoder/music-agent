import asyncio

from dotenv import load_dotenv, find_dotenv

from chat.llm.graph import init_graph
from chat.service.music import aload_local_music
from core.db.postgres import init_db, run_migrations
from core.llm.memory.postgres import init_memory
from core.logger.logger import logger

if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass
    logger.info("Starting up...")
    init_db()
    run_migrations()
    init_memory()
    init_graph()
    asyncio.run(aload_local_music())