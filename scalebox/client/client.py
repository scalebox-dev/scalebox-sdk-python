import os
import sys

from utils.httpxclient import HTTPXClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "generated"))

import asyncio

import httpx
from generated import api_pb2
from generated.api_pb2_connect import AsyncFilesystemClient


# 自定义 HTTP 客户端适配器
class CustomHTTPClient:
    def __init__(self):
        self.client = httpx.Client()

    def request(self, method, url, headers, content, timeout, extensions):
        # 移除可能导致问题的参数或调整调用方式
        # 根据 ConnectRPC 的实际需求调整
        try:
            response = self.client.request(
                method=method,
                url=url,
                headers=headers,
                content=content,
                timeout=timeout,
            )
            return response
        except TypeError as e:
            # 如果仍然有参数问题，尝试不同的调用方式
            if "unexpected keyword argument" in str(e):
                # 移除有问题的参数
                kwargs = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "content": content,
                    "timeout": timeout,
                }
                # 移除可能引起问题的参数
                if "body" in str(e):
                    kwargs.pop("content", None)

                response = self.client.request(**kwargs)
                return response
            raise


async def main():
    # 创建客户端
    client = AsyncFilesystemClient(
        base_url="http://localhost:8080", http_client=HTTPXClient
    )

    # 调用服务器流式方法
    # extra = {"Authorization": "Bearer root","Transfer-Encoding":"chunked",
    #          "Keepalive-Ping-Interval":1000}
    extra = {"Authorization": "Bearer root"}
    # resp=fs_cli.stat(api_pb2.StatRequest(path="/root/Dockerfile"),extra_headers=extra)
    # print(resp)
    # print(resp.entry)
    # stream = fs_cli.watch_dir(api_pb2.WatchDirRequest(path="/root"), extra_headers=extra)
    # request = RequestType(your_field="value")

    # 处理流式响应
    async for response in client.watch_dir(
        api_pb2.WatchDirRequest(path="/root"), extra_headers=extra
    ):
        print(f"Received: {response}")
        # 处理每个响应项


if __name__ == "__main__":
    asyncio.run(main())

# print("Available protocol options:")
# print(f"CONNECT_PROTOBUF: {ConnectProtocol.CONNECT_PROTOBUF}")
# print(f"CONNECT_JSON: {ConnectProtocol.CONNECT_JSON}")
# # print(f"GRPC_PROTOBUF: {ConnectProtocol.GRPC_PROTOBUF}")
# # print(f"GRPC_JSON: {ConnectProtocol.GRPC_JSON}")
# BASE = "http://localhost:8080"
# # client = CustomHTTPClient()
# fs_cli=FilesystemClient(base_url=BASE,protocol=ConnectProtocol.CONNECT_PROTOBUF)
# # extra = {"Authorization": "Bearer root","Transfer-Encoding":"chunked",
# #          "Keepalive-Ping-Interval":1000}
# extra = {"Authorization": "Bearer root"}
# # resp=fs_cli.stat(api_pb2.StatRequest(path="/root/Dockerfile"),extra_headers=extra)
# # print(resp)
# # print(resp.entry)
# stream=fs_cli.watch_dir(api_pb2.WatchDirRequest(path="/root"),extra_headers=extra)
# # 3. 消费流
# print("-------------------------")
# for resp in stream:
#     # resp 就是 api_pb2.WatchDirResponse
#     print(resp)
#
# # 4. 检查错误（可选）
# if stream.error():
#     raise stream.error()
