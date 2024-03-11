from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class VideoFrame(_message.Message):
    __slots__ = ["data", "is_final"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    IS_FINAL_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    is_final: bool
    def __init__(self, data: _Optional[bytes] = ..., is_final: bool = ...) -> None: ...

class ProcessedVideoFrame(_message.Message):
    __slots__ = ["data", "is_final"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    IS_FINAL_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    is_final: bool
    def __init__(self, data: _Optional[bytes] = ..., is_final: bool = ...) -> None: ...
