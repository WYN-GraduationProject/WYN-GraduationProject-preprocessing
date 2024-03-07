from concurrent import futures
import grpc
import cv2
import numpy as np

from proto.video_service.video_service_pb2_grpc import VideoServiceServicer
from proto.video_service.video_service_pb2_grpc import add_VideoServiceServicer_to_server
from proto.video_service.video_model_pb2 import ProcessedVideoFrame


class VideoProcessingService(VideoServiceServicer):
    def ProcessVideo(self, request_iterator, context):
        try:
            for request in request_iterator:
                try:
                    # 将字节转换为numpy数组
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
            context.abort(grpc.StatusCode.INTERNAL, str(e))
            print(e)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_VideoServiceServicer_to_server(
        VideoProcessingService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at [::]:50051")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
