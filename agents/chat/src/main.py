import uvicorn
from fastapi import FastAPI

from base.core.src.config.config import load_config

load_config()

app = FastAPI()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
