from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import core.config  # noqa: F401
from core.logger.logger import logger
from core.client.redis import ainit_redis
from core.memory.async_memory import ainit_memory
from chat.llm.graph import ainit_graph

from chat.router.chat import router
from core.middleware.middleware import ContextHolderMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await ainit_redis()
    await ainit_memory()
    await ainit_graph()
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
