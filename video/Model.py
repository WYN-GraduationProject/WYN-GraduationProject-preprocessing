from pydantic import BaseModel
from typing import List, Optional
from concurrent import futures

import cv2 as cv
import grpc
import numpy as np
import os
import time


class VideoModel:
    """
    视频实体类
    """
    path: str = None
    """视频路径"""
    filename: str = None
    """视频文件名"""
    data: Optional[List[bytes]] = None
    """视频数据"""
    id: Optional[str] = None
    """视频ID"""

    def __init__(self, path: str, filename: str, data: Optional[List[bytes]] = None, id: Optional[str] = None) -> None:
        super().__init__()
        self.path = path
        self.filename = filename
        self.data = data
        self.id = id

    async def save(self):
        """
        保存视频到本地
        :return: None
        """
        if not self.data:
            print(f"保存文件失败：{self.filename}，没有数据")
            return
        os.makedirs(self.path, exist_ok=True)
        filepath = os.path.join(self.path, self.filename)

        first_frame = np.frombuffer(self.data[0], dtype=np.uint8)
        first_frame = cv.imdecode(first_frame, cv.IMREAD_COLOR)
        height, width, _ = first_frame.shape

        fourcc = cv.VideoWriter.fourcc(*'mp4v')
        out = cv.VideoWriter(filepath, fourcc, 20.0, (width, height))

        for frame_bytes in self.data:
            frame = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv.imdecode(frame, cv.IMREAD_COLOR)
            if frame is not None:
                out.write(frame)

        out.release()
        print(f"保存文件成功：{filepath}")
