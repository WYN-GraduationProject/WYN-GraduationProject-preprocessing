import os
import uuid

import cv2
import numpy as np
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from typing import Tuple

from starlette.background import BackgroundTask
from proto.video_service.video_model_pb2 import VideoFrame
from utils.tools.LoggingFormatter import LoggerManager
from utils.tools.gRPCManager import GrpcManager

router = APIRouter(
    prefix="/api/video-pre",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)

logger = LoggerManager(logger_name="video_api").get_logger()


def get_grpc_manager():
    """
    获取gRPC管理器
    :return: gRPC管理器
    """
    return GrpcManager()


async def process_video(video_path, video_id, grpc_manager):
    """
    处理视频
    :param video_id: 视频ID
    :param video_path: 存储视频的路径
    :param grpc_manager: gRPC管理器
    :return:
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    logger.info(f"Video FPS: {fps}")
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return
    async with grpc_manager.get_stub('video_pre_service') as stub:
        async def request_generator():
            """
            请求生成器
            :return: 视频处理的请求
            """
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                _, img = cv2.imencode('.jpg', frame)
                img_bytes = img.tobytes()
                yield VideoFrame(data=img_bytes, is_final=False, video_id=video_id)
            yield VideoFrame(is_final=True, fps=fps, video_id=video_id)

        try:
            response_stream = stub.ProcessVideo(request_generator())
            async for response in response_stream:
                response_frame = np.frombuffer(response.data, dtype=np.uint8)
                response_frame = cv2.imdecode(response_frame, cv2.IMREAD_GRAYSCALE)
                _, response_img = cv2.imencode('.jpg', response_frame)
                response_img_bytes = response_img.tobytes()
                video_preprocessing_path = response.video_path
            return video_preprocessing_path
        except Exception as e:
            logger.error(f"Failed to process video: {e}")
        finally:
            cap.release()


async def save_video(video: UploadFile) -> Tuple[str, str]:
    video_id = str(uuid.uuid4())
    video_filename = f"{video_id}.mp4"
    video_save_path = f"video_data/original/"
    # 创建保存视频的目录
    os.makedirs(video_save_path, exist_ok=True)
    # 保存上传的视频到文件
    filepath = os.path.join(video_save_path, video_filename)
    with open(filepath, "wb") as f:
        f.write(await video.read())
    # 打印文件路径和视频文件名
    logger.info(f"Saved video to {filepath}")

    return video_save_path + video_filename, video_id


@router.post("/test")
async def upload_video(video: UploadFile = File(...), grpc_manager: GrpcManager = Depends(get_grpc_manager)):
    # 传递视频文件路径给处理函数
    video_path, video_id = await save_video(video)
    file_name = await process_video(video_path, video_id, grpc_manager)
    response = FileResponse(file_name, media_type="video/mp4", filename="video.mp4",
                            background=BackgroundTask(lambda: os.remove(file_name)))
    return response
