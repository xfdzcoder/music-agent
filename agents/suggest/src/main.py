import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

loaded = load_dotenv(os.path.join(os.path.dirname(__file__), ".env.dev"))
if not loaded:
    raise RuntimeError(".env.dev not found")



from router.suggest import router

app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
