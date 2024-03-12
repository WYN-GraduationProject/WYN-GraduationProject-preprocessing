import cv2
import numpy as np
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse

from proto.video_service.video_model_pb2 import VideoFrame
from utils.tools.LoggingFormatter import LoggerManager
from utils.tools.gRPCManager import GrpcManager

router = APIRouter(
    prefix="/video",
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


async def process_video(video_path, grpc_manager):
    """
    处理视频
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
                yield VideoFrame(data=img_bytes, is_final=False)
            yield VideoFrame(is_final=True, fps=fps)

        try:
            request_stream = stub.ProcessVideo(request_generator())
            async for response in request_stream:
                response_frame = np.frombuffer(response.data, dtype=np.uint8)
                response_frame = cv2.imdecode(response_frame, cv2.IMREAD_COLOR)
                _, response_img = cv2.imencode('.jpg', response_frame)
                response_img_bytes = response_img.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + response_img_bytes + b'\r\n')
        except Exception as e:
            logger.error(f"Failed to process video: {e}")
        finally:
            cap.release()


@router.get("/test")
async def test(grpc_manager: GrpcManager = Depends(get_grpc_manager)):
    video_path = "video/test/video_data/test.mp4"
    return StreamingResponse(process_video(video_path, grpc_manager),
                             media_type="multipart/x-mixed-replace; boundary=frame")


# 定义一个FastAPI路由，用于呈现网站页面。
@router.get("/")
async def root():
    """呈现网站页面。"""
    html = """
    <html>
        <head>
            <title>RTSP Video Streaming</title>
        </head>
        <body>
            <h1>RTSP Video Streaming</h1>
            <img src="/video/test">
        </body>
    </html>
    """
    return Response(content=html, media_type="text/html")
