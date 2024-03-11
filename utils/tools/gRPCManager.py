from contextlib import asynccontextmanager

from utils.tools.NacosManager import NacosManager, _NACOS_MANAGER
from utils.tools.ServiceHandler import ServiceHandler
from utils.tools.Singleton import singleton

from grpc.aio import insecure_channel

import yaml

__all__ = ['GrpcManager']


@singleton
class GrpcManager:
    """
    gRPC服务管理器类(单例)
    """

    def __init__(self, nacos_manager: NacosManager = _NACOS_MANAGER):
        # 初始化时创建每个ServiceHandler子类的实例
        self.service_instances = [cls() for cls in ServiceHandler.__subclasses__()]
        all_options = nacos_manager.get_config_utils("MicoService").get_config()
        config = yaml.safe_load(all_options)
        self._service_host = {}
        self._service_ports = {}
        for service in config['ServiceSetting']:
            for service_name, details in service.items():
                self._service_host.update({
                    service_name + "_host": details['host']
                })
                self._service_ports.update({
                    service_name + "_port": details['port']
                })

    def get_service_config(self, service: str):
        return (self._service_host[service + "_host"],
                self._service_ports[service + "_port"])

    @asynccontextmanager
    async def get_stub(self, service: str):
        for instance in self.service_instances:
            if instance.support(name=service):
                target = instance.get_stub_class()
                if target is not None:
                    host, port = self.get_service_config(service)
                    target_url = host + ":" + str(port)
                    async with insecure_channel(target_url) as channel:
                        yield target(channel)


if __name__ == "__main__":
    GrpcManager()
    print("done")
