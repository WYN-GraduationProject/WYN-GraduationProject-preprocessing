from proto.video_service import video_service_pb2_grpc as video_grpc


class ServiceHandler:
    def support(self, name: str) -> bool:
        pass

    def get_service_name(self) -> str:
        pass

    def get_stub_class(self):
        pass


class VideoPreServiceHandler(ServiceHandler):
    def support(self, name: str) -> bool:
        return name == 'video_pre_service'

    def get_service_name(self) -> str:
        return 'video_pre_service'

    def get_stub_class(self):
        return video_grpc.VideoServiceStub
