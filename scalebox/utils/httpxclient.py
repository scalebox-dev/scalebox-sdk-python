import asyncio
import contextlib
import json
from typing import Any, AsyncGenerator, Dict, Generator, Optional, Union

import httpx


class HTTPXClient:
    """
    基于 httpx.AsyncClient 的高级 HTTP 工具类
    支持同步/异步请求、连接池管理、流式传输等完整功能
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 50,
        keepalive_expiry: float = 5.0,
        http2: bool = False,
        ssl_verify: bool = True,
        default_headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
        retries: int = 0,
        backoff_factor: float = 0.1,
    ):
        """
        初始化 HTTP 客户端

        :param base_url: 基础 URL 前缀
        :param timeout: 请求超时时间(秒)
        :param max_connections: 最大连接数
        :param max_keepalive_connections: 最大空闲连接数
        :param keepalive_expiry: 空闲连接超时时间(秒)
        :param http2: 是否启用 HTTP/2
        :param ssl_verify: 是否验证 SSL 证书
        :param default_headers: 默认请求头
        :param follow_redirects: 是否跟随重定向
        :param retries: 请求失败重试次数
        :param backoff_factor: 重试退避因子
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.http2 = http2
        self.ssl_verify = ssl_verify
        self.default_headers = default_headers or {}
        self.follow_redirects = follow_redirects
        self.retries = retries
        self.backoff_factor = backoff_factor

        # 创建同步客户端
        self.sync_client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                keepalive_expiry=keepalive_expiry,
            ),
            http2=http2,
            verify=ssl_verify,
            headers=self.default_headers,
            follow_redirects=follow_redirects,
        )

        # 创建异步客户端
        self.async_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                keepalive_expiry=keepalive_expiry,
            ),
            http2=http2,
            verify=ssl_verify,
            headers=self.default_headers,
            follow_redirects=follow_redirects,
        )

        # 配置重试
        if retries > 0:
            retry_transport = httpx.HTTPTransport(
                retries=self.retries, backoff_factor=self.backoff_factor
            )
            async_retry_transport = httpx.AsyncHTTPTransport(
                retries=self.retries, backoff_factor=self.backoff_factor
            )

            self.sync_client = httpx.Client(transport=retry_transport)
            self.async_client = httpx.AsyncClient(transport=async_retry_transport)

    def close(self) -> None:
        """关闭同步客户端"""
        self.sync_client.close()

    async def aclose(self) -> None:
        """关闭异步客户端"""
        await self.async_client.aclose()

    @contextlib.contextmanager
    def context(self) -> "HTTPXClient":
        """
        同步上下文管理器 (自动关闭)

        使用示例:
        with HTTPXClient() as client:
            response = client.get("/api")
        """
        try:
            yield self
        finally:
            self.close()

    @contextlib.asynccontextmanager
    async def acontext(self) -> "HTTPXClient":
        """
        异步上下文管理器 (自动关闭)

        使用示例:
        async with HTTPXClient() as client:
            response = await client.aget("/api")
        """
        try:
            yield self
        finally:
            await self.aclose()

    @contextlib.contextmanager
    def stream(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
    ) -> Generator[httpx.Response, None, None]:
        """
        同步流式请求上下文管理器

        使用示例:
        with client.stream("GET", "/large-file") as response:
            for chunk in response.iter_bytes():
                process_chunk(chunk)
        """
        headers = headers or {}
        with self.sync_client.stream(
            method,
            url,
            params=params,
            headers={**self.default_headers, **headers},
            json=json_data,
            data=data,
        ) as response:
            yield response

    @contextlib.asynccontextmanager
    async def astream(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
    ) -> AsyncGenerator[httpx.Response, None]:
        """
        异步流式请求上下文管理器

        使用示例:
        async with client.astream("GET", "/large-file") as response:
            async for chunk in response.aiter_bytes():
                process_chunk(chunk)
        """
        headers = headers or {}
        async with self.async_client.stream(
            method,
            url,
            params=params,
            headers={**self.default_headers, **headers},
            json=json_data,
            data=data,
        ) as response:
            yield response

    # ================ 同步请求方法 ================
    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
    ) -> httpx.Response:
        """同步 HTTP 请求"""
        headers = headers or {}
        return self.sync_client.request(
            method,
            url,
            params=params,
            headers={**self.default_headers, **headers},
            json=json_data,
            data=data,
        )

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """同步 GET 请求"""
        return self.request("GET", url, params=params, headers=headers)

    def post(
        self,
        url: str,
        json_data: Optional[Any] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """同步 POST 请求"""
        return self.request(
            "POST", url, params=params, headers=headers, json_data=json_data, data=data
        )

    def put(
        self,
        url: str,
        json_data: Optional[Any] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """同步 PUT 请求"""
        return self.request(
            "PUT", url, params=params, headers=headers, json_data=json_data, data=data
        )

    def delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """同步 DELETE 请求"""
        return self.request("DELETE", url, params=params, headers=headers)

    # ================ 异步请求方法 ================
    async def arequest(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Any] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
    ) -> httpx.Response:
        """异步 HTTP 请求"""
        headers = headers or {}
        return await self.async_client.request(
            method,
            url,
            params=params,
            headers={**self.default_headers, **headers},
            json=json_data,
            data=data,
        )

    async def aget(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """异步 GET 请求"""
        return await self.arequest("GET", url, params=params, headers=headers)

    async def apost(
        self,
        url: str,
        json_data: Optional[Any] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """异步 POST 请求"""
        return await self.arequest(
            "POST", url, params=params, headers=headers, json_data=json_data, data=data
        )

    async def aput(
        self,
        url: str,
        json_data: Optional[Any] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """异步 PUT 请求"""
        return await self.arequest(
            "PUT", url, params=params, headers=headers, json_data=json_data, data=data
        )

    async def adelete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """异步 DELETE 请求"""
        return await self.arequest("DELETE", url, params=params, headers=headers)

    # ================ 响应处理工具 ================
    @staticmethod
    def read_response(response: httpx.Response) -> bytes:
        """读取完整响应内容 (同步)"""
        return response.content

    @staticmethod
    def read_response_text(response: httpx.Response) -> str:
        """读取响应文本 (同步)"""
        return response.text

    @staticmethod
    def read_response_json(response: httpx.Response) -> Any:
        """解析 JSON 响应 (同步)"""
        return response.json()

    @staticmethod
    async def aread_response(response: httpx.Response) -> bytes:
        """异步读取完整响应内容"""
        return await response.aread()

    @staticmethod
    async def aread_response_text(response: httpx.Response) -> str:
        """异步读取响应文本"""
        return await response.atext()

    @staticmethod
    async def aread_response_json(response: httpx.Response) -> Any:
        """异步解析 JSON 响应"""
        return await response.ajson()

    # ================ 连接池状态 ================
    def connection_pool_status(self) -> Dict[str, Any]:
        """获取同步连接池状态"""
        transport = self.sync_client._transport
        return {
            "total_connections": transport._pool.num_connections,
            "active_connections": transport._pool.num_active_connections,
            "idle_connections": transport._pool.num_idle_connections,
            "max_connections": transport._pool.max_connections,
        }

    async def aconnection_pool_status(self) -> Dict[str, Any]:
        """获取异步连接池状态"""
        transport = self.async_client._transport
        return {
            "total_connections": transport._pool.num_connections,
            "active_connections": transport._pool.num_active_connections,
            "idle_connections": transport._pool.num_idle_connections,
            "max_connections": transport._pool.max_connections,
        }

    # ================ 高级功能 ================
    def set_proxy(self, proxy_url: str, proxy_auth: Optional[tuple] = None) -> None:
        """设置代理 (同步和异步)"""
        self.sync_client = httpx.Client(proxies=proxy_url, auth=proxy_auth)
        self.async_client = httpx.AsyncClient(proxies=proxy_url, auth=proxy_auth)

    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """设置 Cookies (同步和异步)"""
        self.sync_client.cookies = httpx.Cookies(cookies)
        self.async_client.cookies = httpx.Cookies(cookies)

    def add_event_hook(self, event: str, hook: callable) -> None:
        """添加事件钩子 (同步和异步)"""
        self.sync_client.event_hooks[event].append(hook)
        self.async_client.event_hooks[event].append(hook)

    def reset_client(self) -> None:
        """重置客户端 (清除所有状态)"""
        self.close()
        self.async_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            http2=self.http2,
            verify=self.ssl_verify,
            headers=self.default_headers,
        )
        self.sync_client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            http2=self.http2,
            verify=self.ssl_verify,
            headers=self.default_headers,
        )
