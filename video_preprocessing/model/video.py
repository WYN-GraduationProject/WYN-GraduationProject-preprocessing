import os
from typing import List, Optional
from utils.tools.LoggingFormatter import LoggerManager
import cv2 as cv
import numpy as np

logger = LoggerManager(logger_name="VideoModel").get_logger()


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
            logger.error(f"视频保存失败：{self.filename}，没有数据")
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
        logger.info(f"视频保存成功：{self.path}/{self.filename}")
