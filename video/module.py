from pydantic import BaseModel
from typing import List, Optional
from concurrent import futures

import cv2 as cv
import grpc
import numpy as np
import os
import time
import uuid

import pyproto.video.video_pb2 as video_pb2
import pyproto.video.video_pb2_grpc as video_pb2_grpc


class Video(BaseModel):
    path: str = None
    filename: str
    data: Optional[List[bytes]] = None
    id: Optional[str] = None

    def __init__(self, path: str, filename: str, data: Optional[List[bytes]] = None, id: Optional[str] = None) -> None:
        super().__init__()
        self.path = path
        self.filename = filename
        self.data = data
        self.id = id

    async def save(self):
        if self.data:
            printf("保存文件" + self.filename)
        else:
            printf("保存文件失败" + self.filename)


class VideoProcessingService(video_pb2_grpc.VideoProcessingServiceServicer):
    def ProcessVideo(self, request, context):
        video_grpc = request.video
        video = Video(path=video_grpc.path, filename=video_grpc.filename, data=video_grpc.data, id=video_grpc.id)
