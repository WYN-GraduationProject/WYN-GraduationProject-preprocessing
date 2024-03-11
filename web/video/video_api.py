import uuid

from utils.tools.FPSCalculator import FPSCalculator
from video.Model import VideoModel
from fastapi import APIRouter

from proto.video_service.video_model_pb2 import VideoFrame

import cv2

router = APIRouter()
cap = cv2.VideoCapture(0)  # 尝试使用0作为摄像头索引
if not cap.isOpened():
    print("Error: Could not open video device.")
    exit(1)

def request_generator(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        print("Failed to encode frame")
        return None
    yield VideoFrame(data=buffer.tobytes())

@router.get("/")
async def open_camera(stub):
    fps_calculator = FPSCalculator()
    video_id = str(uuid.uuid4())
    video_path = f"video_data/{video_id}"
    video_filename = f"{video_id}.mp4"
    video = VideoModel(video_path, video_filename, video_id, [], 30)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        fps = await fps_calculator.update()

        # 将FPS信息添加到帧上
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # 显示原始帧
        cv2.imshow('Original Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 如果按下'q'则退出
            break
        async for res in stub.ProcessVideo(request_generator(frame)):
            video.fps = fps
            video.data.append(res.data)
    await video.save()