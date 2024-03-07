import uuid
import numpy as np
import cv2

import grpc

from proto.video_service.video_model_pb2 import ProcessedVideoFrame
from proto.video_service.video_service_pb2_grpc import VideoServiceServicer
from video.Model import VideoModel


class VideoProcessingServicer(VideoServiceServicer):
    def ProcessVideo(self, request_iterator, context):
        try:
            # video_id = str(uuid.uuid1())
            # video_path = f"video/{video_id}"
            # video = VideoModel(video_path, f"{video_id}.mp4", id=video_id)
            for request in request_iterator:
                try:
                    nparr = np.frombuffer(request.data, np.uint8)
                    print("接收到来自客户端的数据：", nparr.size, "bytes:", nparr[:10], "...")
                    if nparr.size == 0:
                        context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Empty frame data.")
                    # 将numpy数组转换为OpenCV图像
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
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
        except Exception as e:
            context.abort(grpc.StatusCode.UNKNOWN, str(e))
            print(e)
