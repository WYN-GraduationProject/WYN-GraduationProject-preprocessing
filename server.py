import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.tools.LoggingFormatter import ColorFormatter, LoggerManager
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


if __name__ == "__main__":
    logger.info("服务启动...")
    uvicorn.run(app, host="localhost", port=8000)
