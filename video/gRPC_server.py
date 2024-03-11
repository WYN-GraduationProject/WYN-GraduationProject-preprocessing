import asyncio
import logging
import grpc

from concurrent import futures
from Servicer.VideoProcessingServicer import VideoProcessingServicer
from proto.video_service.video_service_pb2_grpc import add_VideoServiceServicer_to_server
from utils.tools.gRPCManager import GrpcManager
from utils.tools.NacosManager import NacosManager


async def serve():
    port = GrpcManager().get_service_config('video_pre_service')[1]
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    add_VideoServiceServicer_to_server(VideoProcessingServicer(), server)
    server.add_insecure_port('[::]:' + str(port))
    NacosManager().get_server_utils("video_pre_service", "localhost", port).register_service()
    # 启动心跳发送任务
    heartbeat_task = asyncio.create_task(send_heartbeat(30, port))
    await server.start()
    await server.wait_for_termination()


async def send_heartbeat(interval=30, port=8000):
    while True:
        try:
            # 假设 NacosManager 有一个 send_heartbeat 方法
            NacosManager().get_server_utils("video_pre_service", "localhost", port).beat()
            print("心跳发送成功")
        except Exception as e:
            print(f"发送心跳失败: {e}")
        await asyncio.sleep(interval)  # 等待指定的时间间隔


if __name__ == '__main__':
    print("服务启动...")
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
