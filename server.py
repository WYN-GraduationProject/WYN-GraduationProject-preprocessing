import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.tools.LoggingFormatter import LoggerManager
from utils.tools.NacosManager import NacosManager, NacosServerUtils
from web.video import video_api

app = FastAPI()

# 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

app.include_router(video_api.router)

logger = LoggerManager(logger_name="server").get_logger()

nacos_serverutils: NacosServerUtils = None  # 定义变量以便在事件处理器中引用


@app.on_event("startup")
async def startup_event():
    global nacos_serverutils
    nacos_serverutils = NacosManager().get_server_utils("video_pre_service", "localhost", 8000)
    # 注册服务
    await nacos_serverutils.register_service()  # 确保这是异步的，或者使用适当的同步调用
    # 启动心跳发送任务，假设 beat 是异步方法
    asyncio.create_task(nacos_serverutils.beat(10))


@app.on_event("shutdown")
async def shutdown_event():
    # 取消注册服务
    nacos_serverutils.deregister_service()
    pass


# @app.post("/upload/")
# async def create_upload_file(file: UploadFile = File(...)):
#     # 读取视频文件
#     contents = await file.read()
#     temp_filename = "temp_" + file.filename
#     with open(temp_filename, "wb") as f:
#         f.write(contents)
#
#     # 灰度处理第一帧
#     cap = cv2.VideoCapture(temp_filename)
#     success, frame = cap.read()
#     if not success:
#         return {"error": "Failed to read video"}
#
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     # 确保保存为正确的图像格式
#     _, ext = os.path.splitext(file.filename)
#     valid_ext = ext.lower() in [".png", ".jpg", ".jpeg"]
#     gray_filename = "gray_" + (file.filename if valid_ext else file.filename.rsplit(".", 1)[0] + ".png")
#     cv2.imwrite(gray_filename, gray)
#
#     cap.release()
#
#     # 清理临时视频文件
#     os.remove(temp_filename)
#
#     # 返回处理后的图像文件
#     return FileResponse(gray_filename)


if __name__ == "__main__":
    logger.info("服务启动...")
    uvicorn.run(app, host="localhost", port=8000)
