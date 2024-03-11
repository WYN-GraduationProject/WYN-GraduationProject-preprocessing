from fastapi import Depends, FastAPI
from web.video import video_api
from utils.tools.NacosManager import NacosManager

import uvicorn

app = FastAPI()

app.include_router(video_api.router)

if __name__ == "__main__":
    NacosManager().get_server_utils("video_pre_service", "localhost", 8000).register_service()
    uvicorn.run(app, host="localhost", port=8000)
