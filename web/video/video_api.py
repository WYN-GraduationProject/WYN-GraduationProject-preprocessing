import uuid

import cv2
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from proto.video_service.video_model_pb2 import VideoFrame
from utils.tools.gRPCManager import GrpcManager
from video.Model import VideoModel

router = APIRouter(
    prefix="/video",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)


def get_grpc_manager():
    return GrpcManager()


@router.get("/test")
async def test(grpc_manager: GrpcManager = Depends(get_grpc_manager)):
    video_path = "video/test/video_data/test.mp4"
    cap = cv2.VideoCapture(video_path)
    video_id = str(uuid.uuid4())
    video_filename = f"{video_id}.mp4"
    video_save_path = f"video_data/{video_id}"
    video = VideoModel(video_save_path, video_filename, video_id, [], 60)
    while True:
        res, frame = cap.read()
        if not res:
            break
        ret, jpeg = cv2.imencode('.jpg', frame)
        async with grpc_manager.get_stub('video_pre_service') as stub:
            async for res in stub.ProcessVideo(request_generator(frame)):
                video.data.append(res.data)
    await video.save()
    return FileResponse(video_path, media_type="video/mp4")


def request_generator(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        print("Failed to encode frame")
        return None
    yield VideoFrame(data=buffer.tobytes())
