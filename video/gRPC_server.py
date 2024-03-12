import asyncio
import logging
import grpc
import logging

from concurrent import futures
from Servicer.VideoProcessingServicer import VideoProcessingServicer
from proto.video_service.video_service_pb2_grpc import add_VideoServiceServicer_to_server
from utils.tools.LoggingFormatter import ColorFormatter, LoggerManager
from utils.tools.gRPCManager import GrpcManager
from utils.tools.NacosManager import NacosManager

logger = LoggerManager(logger_name="gRPC").get_logger()


async def serve():
    port = GrpcManager().get_service_config('video_pre_service')[1]
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    add_VideoServiceServicer_to_server(VideoProcessingServicer(), server)
    server.add_insecure_port('[::]:' + str(port))
    nacos_serverutils = NacosManager().get_server_utils("video_pre_service", "localhost", port)
    # 注册服务
    await nacos_serverutils.register_service()
    # 启动心跳发送任务
    asyncio.create_task(nacos_serverutils.beat(10))
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logger.info("preprocessing-gRPC服务启动...")
    asyncio.run(serve())
