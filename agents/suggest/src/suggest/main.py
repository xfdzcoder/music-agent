import uvicorn
from fastapi import FastAPI

from core.config.config import load_config

load_config()

from router.suggest import router

app = FastAPI()
app.include_router(router)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
