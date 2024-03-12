import uuid

import cv2
import grpc
import numpy as np
import logging as log

from proto.video_service.video_model_pb2 import ProcessedVideoFrame
from proto.video_service.video_service_pb2_grpc import VideoServiceServicer
from video.Model import VideoModel
from utils.tools.LoggingFormatter import LoggerManager

logger = LoggerManager(logger_name="VideoProcessingServicer").get_logger()


class VideoProcessingServicer(VideoServiceServicer):
    async def ProcessVideo(self, request_iterator, context):
        """
        处理客户端发送的视频流，目前实现了简单的图像处理，例如转灰度图
        :param request_iterator: 流式请求迭代器
        :param context: rpc请求上下文
        """
        video_id = str(uuid.uuid4())
        video_filename = f"{video_id}.mp4"
        video_save_path = f"video_data/{video_id}"
        video = VideoModel(video_save_path, video_filename, video_id, [], 60)
        try:
            async for request in request_iterator:
                logger.info("接收到来自客户端的数据帧{}".format(request.is_final))
                if request.is_final:
                    logger.info("接收到来自客户端的结束帧...")
                    await video.to_gray()
                    await video.save()
                    break

                np_arr = np.frombuffer(request.data, np.uint8)
                logger.info("接收到来自客户端的数据：{} bytes: {}...".format(np_arr.size, np_arr[:10]))

                if np_arr.size == 0:
                    logger.error("Empty frame data.")
                    context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Empty frame data.")

                # 将numpy数组转换为OpenCV图像
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if img is None or img.size == 0:
                    logger.error("Cannot decode frame data.")
                    context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Cannot decode frame data.")

                # 将图像数据添加到视频实体中
                video.data.append(request.data)
                # 返回处理后的图像数据
                # yield ProcessedVideoFrame(data=video.data[-1])
        except Exception as e:
            context.abort(grpc.StatusCode.UNKNOWN, str(e))
            logger.error("处理视频流时发生错误：{}".format(e))
