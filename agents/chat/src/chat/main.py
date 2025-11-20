from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import core.config  # noqa: F401
from core.db.postgres import init_db, run_migrations
from core.llm.memory.postgres import init_memory
from core.logger.logger import logger
from chat.llm.graph import init_graph
from chat.service.music import aload_local_music

from chat.router.chat import router
from core.middleware.middleware import ContextHolderMiddleware


@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    logger.info("Starting up...")
    init_db()
    run_migrations()
    init_memory()
    init_graph()
    await aload_local_music()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(ContextHolderMiddleware)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=18000,
        log_config=None,
    )
