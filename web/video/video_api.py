import asyncio
import logging

import cv2
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from proto.video_service.video_model_pb2 import VideoFrame
from utils.tools.gRPCManager import GrpcManager
from utils.tools.LoggingFormatter import LoggerManager

router = APIRouter(
    prefix="/video",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)

logger = LoggerManager(logger_name="video_api").get_logger()


def get_grpc_manager():
    return GrpcManager()


async def process_video(video_path, grpc_manager):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return
    async with grpc_manager.get_stub('video_pre_service') as stub:
        async def request_generator():
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                _, img = cv2.imencode('.jpg', frame)
                img_bytes = img.tobytes()
                yield VideoFrame(data=img_bytes, is_final=False)
            yield VideoFrame(is_final=True)

        try:
            request_stream = stub.ProcessVideo(request_generator())
            async for response in request_stream:
                pass
        except Exception as e:
            logger.error(f"Failed to process video: {e}")
        finally:
            cap.release()


@router.get("/test")
async def test(grpc_manager: GrpcManager = Depends(get_grpc_manager)):
    video_path = "video/test/video_data/test.mp4"
    await process_video(video_path, grpc_manager)
    return FileResponse(video_path, media_type="video/mp4")
