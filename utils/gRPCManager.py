from contextlib import asynccontextmanager
from typing import Tuple

from grpc.aio import insecure_channel

from .ConfigHandler import _CONFIG_HANDLER, ConfigHandler
from .Singleton import Singleton

__all__ = ['gRPCManager', 'MockGRPCManager']

from ..service import ServiceEnum


class gRPCManager(metaclass=Singleton):
    def __init__(self, handler: ConfigHandler = _CONFIG_HANDLER):
        all_options = handler.get_options('ServiceSetting')

        service_hosts = list(filter(lambda x: x.endswith('_service_host'), all_options))
        service_ports = list(filter(lambda x: x.endswith('_service_port'), all_options))
        self._service_host = {}
        self._service_ports = {}

        for host in service_hosts:
            self._service_host.update({
                host: handler.get_config("ServiceSetting", host)
            })

        for port in service_ports:
            self._service_ports.update({
                port: handler.get_config("ServiceSetting", port)
            })

    def get_service_config(self, service: ServiceEnum) -> Tuple[str, str]:
        return (self._service_host[service.service_name + "_service_host"],
                self._service_ports[service.service_name + "_service_port"])

    @asynccontextmanager
    async def get_stub(self, service: ServiceEnum):
        if service.is_http_service:
            raise RuntimeError("该服务不是gRPC服务")

        target = service._get_stub_class()

        if target is not None:
            host = self._service_host[service.service_name + "_service_host"]
            port = self._service_ports[service.service_name + "_service_port"]
            target_url = host + ":" + port
            async with insecure_channel(target_url) as channel:
                yield target(channel)


class MockGRPCManager(gRPCManager):
    @asynccontextmanager
    async def get_stub(self, service: ServiceEnum):
        yield service._get_mock_stub_class()()
