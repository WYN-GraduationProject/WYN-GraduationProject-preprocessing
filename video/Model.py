import logging
import os
from typing import List, Optional

import cv2 as cv
import numpy as np


class VideoModel:
    """
    视频实体类
    """
    fps: int = 30
    """视频帧率"""
    path: Optional[str] = None
    """视频保存路径"""
    filename: Optional[str] = None
    """视频文件名"""
    data: Optional[List[bytes]] = None
    """视频数据"""
    id: Optional[str] = None
    """视频唯一ID"""

    def __init__(self, path: str, filename: str, id: str, data: List[bytes], fps: int = 30):
        """
        初始化视频实体
        :param path: 视频保存路径
        :param filename: 视频文件名
        :param id: 视频唯一ID
        :param data: 视频数据
        :param fps: 视频帧率
        """
        self.path = path
        self.filename = filename
        self.id = id
        self.data = data
        self.fps = fps

    async def save(self):
        """
        保存视频到本地
        :return: None
        """
        if not self.data:
            logging.log(logging.ERROR, f"保存文件失败：{self.filename}，没有数据")
            return
        os.makedirs(self.path, exist_ok=True)
        filepath = os.path.join(self.path, self.filename)

        first_frame = np.frombuffer(self.data[0], dtype=np.uint8)
        first_frame = cv.imdecode(first_frame, cv.IMREAD_COLOR)
        height, width, _ = first_frame.shape

        fourcc = cv.VideoWriter.fourcc(*'mp4v')
        out = cv.VideoWriter(filepath, fourcc, self.fps, (width, height))

        for frame_bytes in self.data:
            frame = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv.imdecode(frame, cv.IMREAD_COLOR)
            if frame is not None:
                out.write(frame)

        out.release()
        logging.log(logging.INFO, f"视频保存成功：{filepath}")

    async def to_gray(self):
        """
        将视频转换为灰度视频
        :return: None
        """
        if not self.data:
            logging.log(logging.ERROR, f"转换为灰度视频失败：{self.filename}，没有数据")
            return
        gray_data = []
        for frame_bytes in self.data:
            frame = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv.imdecode(frame, cv.IMREAD_COLOR)
            if frame is not None:
                gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                _, img_encoded = cv.imencode('.jpg', gray_frame)
                gray_data.append(img_encoded.tobytes())
        self.data = gray_data
        logging.log(logging.INFO, f"视频转换为灰度视频成功：{self.filename}")

