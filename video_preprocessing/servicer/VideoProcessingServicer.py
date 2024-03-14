import uuid

import cv2
import grpc
import numpy as np

from typing import Optional
from proto.video_service.video_service_pb2_grpc import VideoServiceServicer
from proto.video_service.video_model_pb2 import ProcessedVideoFrame
from utils.tools.LoggingFormatter import LoggerManager
from video_preprocessing.model.video import VideoModel

logger = LoggerManager(logger_name="VideoProcessingServicer").get_logger()


async def to_gray(frame_bytes: bytes) -> Optional[bytes]:
    """
    将图像数据转换为灰度图
    :return: None
    """
    if not frame_bytes:
        logger.error("Empty frame data.")
        return None
    frame = np.frombuffer(frame_bytes, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, img = cv2.imencode('.jpg', gray)
        return img.tobytes()


class VideoProcessingServicer(VideoServiceServicer):

    async def ProcessVideo(self, request_iterator, context):
        """
        处理客户端发送的视频流，目前实现了简单的图像处理，例如转灰度图
        :param request_iterator: 流式请求迭代器
        :param context: rpc请求上下文
        """
        video = VideoModel("", "", "", [], 30)
        try:
            async for request in request_iterator:
                video.id = request.video_id
                video.filename = f"{video.id}.mp4"
                video.path = (
                    f"/Users/wangyaning/毕业设计/源代码/backend/WYN-GraduationProject-preprocessing/video_data"
                    f"/preprocessing")
                if request.is_final:
                    video.fps = request.fps
                    logger.info("该视频{}的视频帧率为：{}".format(video.id, video.fps))
                    logger.info("接收到来自客户端的结束帧...")

                    # 尽量不要在 rpc 服务中进行文件保存操作，因为这样会阻塞服务
                    await video.save()
                    break

                np_arr = np.frombuffer(request.data, np.uint8)

                if np_arr.size == 0:
                    logger.error("Empty frame data.")
                    context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Empty frame data.")

                # 将numpy数组转换为OpenCV图像
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if img is None or img.size == 0:
                    logger.error("Cannot decode frame data.")
                    context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Cannot decode frame data.")

                # 将 request.data 进行处理，转换为灰度图
                gray_frame = await to_gray(request.data)
                video.data.append(gray_frame)
                # 返回处理后的图像数据
                yield ProcessedVideoFrame(data=gray_frame, video_path=video.path + "/" + video.filename)
        except Exception as e:
            context.abort(grpc.StatusCode.UNKNOWN, str(e))
            logger.error("处理视频流时发生错误：{}".format(e))
