import requests
import socket

nacos_config_server_url = "http://1.94.63.237:8848/nacos/v2/cs/config"
nacos_instance_server_url = "http://1.94.63.237:8848/nacos/v2/ns/instance"

# 设置查询参数
config_params = {
    'dataId': 'WYNbysj',
    'group': 'DEFAULT_GROUP',
    'namespaceId': 'public'
}


# 获取本机IP
def get_host_ip():
    try:
        # 创建一个socket对象
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 尝试连接一个不存在的地址，仅仅是为了触发操作系统提供本机IP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# 使用函数获取当前机器的IP地址
host_ip = get_host_ip()
print(f"本机IP地址: {host_ip}")

# 发起GET请求
config_response = requests.get(nacos_config_server_url, params=config_params)

# 打印响应的文本内容（例如JSON数据）
print(config_response.text)

# 检查状态码，确认请求成功
if config_response.status_code == 200:
    print("请求成功")
else:
    print("请求失败，状态码：", config_response.status_code)

instance_params = {
    'serviceName': 'preprocessing-service',
    'ip': host_ip,
    'port': 8000
}
# 注册实例
instance_response = requests.post(nacos_instance_server_url, params=instance_params)

if instance_response.status_code == 200:
    print("注册实例成功")
    print(instance_response.text)
