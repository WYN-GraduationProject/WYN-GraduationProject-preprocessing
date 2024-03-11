import cv2
import grpc
import numpy as np

from proto.video_service.video_model_pb2 import ProcessedVideoFrame
from proto.video_service.video_service_pb2_grpc import VideoServiceServicer


class VideoProcessingServicer(VideoServiceServicer):
    async def ProcessVideo(self, request_iterator, context):
        """
        处理客户端发送的视频流，目前实现了简单的图像处理，例如转灰度图
        :param request_iterator: 流式请求迭代器
        :param context: rpc请求上下文
        """
        try:
            async for request in request_iterator:
                np_arr = np.frombuffer(request.data, np.uint8)
                print("接收到来自客户端的数据：", np_arr.size, "bytes:", np_arr[:10], "...")
                if np_arr.size == 0:
                    context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Empty frame data.")
                # 将numpy数组转换为OpenCV图像
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if img is None or img.size == 0:
                    context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Cannot decode frame data.")

                # 进行图像处理，例如转灰度图、降噪等
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # 更多图像处理...

                # 将处理后的图像转换为字节
                _, img_encoded = cv2.imencode('.jpg', gray)

                yield ProcessedVideoFrame(data=img_encoded.tobytes())
        except Exception as e:
            context.abort(grpc.StatusCode.UNKNOWN, str(e))
            print(e)
