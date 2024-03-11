from fastapi import Depends, FastAPI
from web.video import video_api

import uvicorn

app = FastAPI()

app.include_router(video_api.router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
