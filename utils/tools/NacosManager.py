import asyncio
import logging

import nacos

from utils.tools.Singleton import singleton

SERVER_ADDRESSES = "1.94.63.237:8848"
NAMESPACE = "public"


class NacosServerUtils:
    """
    Nacos服务注册工具类
    """

    def __init__(self, _client, _service_name, _ip, _port):
        self.client = _client
        self.service_name = _service_name
        self.ip = _ip
        self.port = _port

    async def register_service(self):
        return self.client.add_naming_instance(self.service_name, self.ip, self.port)

    def deregister_service(self):
        return self.client.remove_naming_instance(self.service_name, self.ip, self.port)

    async def beat(self, interval=30):
        while True:
            try:
                self.client.send_heartbeat(self.service_name, self.ip, self.port)
                logging.debug("心跳发送成功")
            except Exception as e:
                logging.error(f"发送心跳失败: {e}")
            await asyncio.sleep(interval)


class NacosConfigUtils:
    """
    Nacos配置工具类
    """

    def __init__(self, client, data_id, group):
        self.client = client
        self.data_id = data_id
        self.group = group

    def get_config(self):
        return self.client.get_config(self.data_id, self.group)

    def publish_config(self, content):
        return self.client.publish_config(self.data_id, self.group, content)

    def remove_config(self):
        return self.client.remove_config(self.data_id, self.group)


@singleton
class NacosManager:
    """
    Nacos管理器类(单例)
    """

    def __init__(self):
        self.client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE)

    def get_server_utils(self, service_name, ip, port):
        return NacosServerUtils(self.client, service_name, ip, port)

    def get_config_utils(self, data_id, group="DEFAULT_GROUP"):
        return NacosConfigUtils(self.client, data_id, group)


_NACOS_MANAGER = NacosManager()
