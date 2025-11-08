from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import core.config  # noqa: F401
from chat.llm.graph import init_graph
from core.logger.logger import logger
from core.memory.memory import init_memory

from chat.router.chat import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await init_memory()
    await init_graph()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18000, log_config=None)
