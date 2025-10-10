# import sys, os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))
import asyncio
import aiohttp
from generated import api_pb2
from generated.api_pb2_connect import AsyncFilesystemClient
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


@retry(
    stop=stop_after_attempt(5),  # 最大重试5次
    wait=wait_exponential(multiplier=1, min=4, max=10),  # 指数退避等待
    retry=retry_if_exception_type(
        (aiohttp.ClientError, asyncio.TimeoutError)
    ),  # 针对这些异常重试
)
async def watch_directory_example():
    # 创建 aiohttp 客户端会话
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=None)
    ) as session:
        # 创建文件系统客户端
        client = AsyncFilesystemClient(
            base_url="http://localhost:8080",
            http_client=session,
            # protocol=ConnectProtocol.CONNECT_PROTOBUF  # 如果需要指定协议
        )
        # extra = {"authorization": "Bearer root"}
        # 创建监视请求
        request = api_pb2.WatchDirRequest(path="/root")

        # 可选：添加额外的请求头
        extra_headers = {
            "Authorization": "Bearer root",
            "X-Custom-Header": "custom-value",
        }

        try:
            # 使用 async for 循环处理流式响应
            async for response in client.watch_dir(
                request, extra_headers=extra_headers
            ):
                print(f"Received event: {response}")
                # 在这里处理每个事件
                # 例如，根据事件类型执行不同的操作

                # 如果收到特定事件，可以中断循环
                # if response.event_type == api_pb2.WatchDirResponse.EVENT_TYPE_STOP:
                #     break

        except Exception as e:
            print(f"Error during directory watching: {e}")

        finally:
            # 关闭会话（在 with 语句中会自动关闭，但这里为了清晰展示）
            await session.close()


async def main():
    # 运行监视示例
    await watch_directory_example()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
