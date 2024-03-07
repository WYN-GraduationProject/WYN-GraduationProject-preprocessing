import asyncio
import cv2
import grpc
import numpy as np
import time  # 引入time模块来计算FPS

from proto.video_service.video_service_pb2_grpc import VideoServiceStub
from proto.video_service.video_model_pb2 import VideoFrame

cap = cv2.VideoCapture(1)  # 尝试使用0作为摄像头索引

if not cap.isOpened():
    print("Error: Could not open video device.")
    exit(1)


def request_generator(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        print("Failed to encode frame")
        return None
    yield VideoFrame(data=buffer.tobytes())


async def display_frames(stub):
    frame_count = 0
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        frame_count += 1  # 更新帧数
        current_time = time.time()
        elapsed = current_time - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0

        # 将FPS信息添加到帧上
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 显示原始帧
        cv2.imshow('Original Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 如果按下'q'则退出
            break
        responses = stub.ProcessVideo(request_generator(frame))
        for res in responses:
            nparr = np.frombuffer(res.data, dtype=np.uint8)
            processed_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # 将FPS信息添加到处理后的帧上
            cv2.putText(processed_frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
                        2)

            # 显示处理后的帧
            cv2.imshow('Processed Frame', processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # 如果按下'q'则退出
                break

    await asyncio.sleep(1 / 120)  # 控制帧速


async def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = VideoServiceStub(channel)
    await display_frames(stub)


if __name__ == '__main__':
    asyncio.run(run())
    cap.release()
    cv2.destroyAllWindows()
