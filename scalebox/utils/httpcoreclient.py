import json
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
import httpcore
import contextlib

class HTTPXCoreTool:
    """
    基于 httpcore 的高级 HTTP 工具类
    支持同步/异步请求、连接池管理、流式传输等
    """

    def __init__(
            self,
            base_url: str = "",
            timeout: float = 10.0,
            max_connections: int = 100,
            max_keepalive_connections: int = 50,
            keepalive_expiry: float = 5.0,
            http2: bool = False,
            ssl_verify: bool = True,
            headers: Optional[Dict[str, str]] = None
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
        :param headers: 默认请求头
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.http2 = http2
        self.ssl_verify = ssl_verify
        self.default_headers = headers or {}

        # 创建同步连接池
        self.sync_pool = httpcore.ConnectionPool(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
            http2=http2,
            ssl_context=None if ssl_verify else httpcore._ssl.create_untrusted_context()
        )

        # 创建异步连接池
        self.async_pool = httpcore.AsyncConnectionPool(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
            http2=http2,
            ssl_context=None if ssl_verify else httpcore._ssl.create_untrusted_context()
        )

    def close(self) -> None:
        """关闭同步连接池"""
        self.sync_pool.close()

    async def aclose(self) -> None:
        """关闭异步连接池"""
        await self.async_pool.aclose()

    @contextlib.contextmanager
    def stream_context(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            content: Optional[Union[bytes, Iterable[bytes]]] = None
    ) -> Iterable[httpcore.Response]:
        """
        同步流式请求上下文管理器

        使用示例:
        with tool.stream_context("GET", "https://example.com") as response:
            for chunk in response.iter_bytes():
                print(chunk)
        """
        full_url = self._build_url(url, params)
        req_headers = self._build_headers(headers)

        response = self.sync_pool.request(
            method=method.encode(),
            url=self._parse_url(full_url),
            headers=req_headers,
            content=content,
            timeout=self.timeout
        )

        try:
            yield response
        finally:
            # 确保流关闭
            for _ in response.stream:
                pass

    @contextlib.asynccontextmanager
    async def async_stream_context(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            content: Optional[Union[bytes, Iterable[bytes]]] = None
    ) -> Iterable[httpcore.Response]:
        """
        异步流式请求上下文管理器

        使用示例:
        async with tool.async_stream_context("GET", "https://example.com") as response:
            async for chunk in response.astream_bytes():
                print(chunk)
        """
        full_url = self._build_url(url, params)
        req_headers = self._build_headers(headers)

        response = await self.async_pool.request(
            method=method.encode(),
            url=self._parse_url(full_url),
            headers=req_headers,
            content=content,
            timeout=self.timeout
        )

        try:
            yield response
        finally:
            # 确保流关闭
            async for _ in response.stream:
                pass

    def request(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            json_data: Optional[Any] = None,
            data: Optional[Union[bytes, Dict[str, Any]]] = None
    ) -> httpcore.Response:
        """
        同步 HTTP 请求
        """
        content, headers = self._prepare_content(json_data, data, headers)
        full_url = self._build_url(url, params)
        req_headers = self._build_headers(headers)

        return self.sync_pool.request(
            method=method.encode(),
            url=self._parse_url(full_url),
            headers=req_headers,
            content=content,
            timeout=self.timeout
        )

    async def async_request(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            json_data: Optional[Any] = None,
            data: Optional[Union[bytes, Dict[str, Any]]] = None
    ) -> httpcore.Response:
        """
        异步 HTTP 请求
        """
        content, headers = self._prepare_content(json_data, data, headers)
        full_url = self._build_url(url, params)
        req_headers = self._build_headers(headers)

        return await self.async_pool.request(
            method=method.encode(),
            url=self._parse_url(full_url),
            headers=req_headers,
            content=content,
            timeout=self.timeout
        )

    # 快捷方法
    def get(self, url: str, **kwargs) -> httpcore.Response:
        return self.request("GET", url, **kwargs)

    async def async_get(self, url: str, **kwargs) -> httpcore.Response:
        return await self.async_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpcore.Response:
        return self.request("POST", url, **kwargs)

    async def async_post(self, url: str, **kwargs) -> httpcore.Response:
        return await self.async_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> httpcore.Response:
        return self.request("PUT", url, **kwargs)

    async def async_put(self, url: str, **kwargs) -> httpcore.Response:
        return await self.async_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> httpcore.Response:
        return self.request("DELETE", url, **kwargs)

    async def async_delete(self, url: str, **kwargs) -> httpcore.Response:
        return await self.async_request("DELETE", url, **kwargs)

    # 辅助方法
    def _build_url(self, url: str, params: Optional[Dict[str, Any]]) -> str:
        """构建完整 URL"""
        if not url.startswith(("http://", "https://")):
            url = f"{self.base_url}/{url.lstrip('/')}"

        if params:
            from urllib.parse import urlencode
            query = urlencode(params, doseq=True)
            url = f"{url}?{query}" if '?' not in url else f"{url}&{query}"

        return url

    def _parse_url(self, url: str) -> Tuple[bytes, bytes, int, bytes]:
        """解析 URL 为 httpcore 格式"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        scheme = parsed.scheme.encode()
        host = parsed.hostname.encode()
        port = parsed.port or (443 if scheme == b"https" else 80)
        path = parsed.path.encode() or b"/"
        if parsed.query:
            path += b"?" + parsed.query.encode()
        return (scheme, host, port, path)

    def _build_headers(self, headers: Optional[Dict[str, str]]) -> List[Tuple[bytes, bytes]]:
        """构建请求头列表"""
        merged_headers = {**self.default_headers, **(headers or {})}
        return [
            (k.lower().encode(), v.encode())
            for k, v in merged_headers.items()
        ]

    def _prepare_content(
            self,
            json_data: Optional[Any],
            data: Optional[Union[bytes, Dict[str, Any]]],
            headers: Optional[Dict[str, str]]
    ) -> Tuple[Optional[Union[bytes, Iterable[bytes]]], Dict[str, str]]:
        """准备请求内容和头信息"""
        content = None
        headers = headers or {}

        if json_data is not None:
            content = json.dumps(json_data).encode('utf-8')
            headers.setdefault("Content-Type", "application/json")

        elif data is not None:
            if isinstance(data, dict):
                from urllib.parse import urlencode
                content = urlencode(data, doseq=True).encode('utf-8')
                headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
            else:
                content = data

        return content, headers

    @staticmethod
    def read_response(response: httpcore.Response) -> bytes:
        """读取完整响应内容"""
        return b"".join(response.stream)

    @staticmethod
    def read_response_json(response: httpcore.Response) -> Any:
        """读取并解析 JSON 响应"""
        return json.loads(HTTPXCoreTool.read_response(response))

    @staticmethod
    async def async_read_response(response: httpcore.Response) -> bytes:
        """异步读取完整响应内容"""
        content = b""
        async for chunk in response.stream:
            content += chunk
        return content

    @staticmethod
    async def async_read_response_json(response: httpcore.Response) -> Any:
        """异步读取并解析 JSON 响应"""
        content = await HTTPXCoreTool.async_read_response(response)
        return json.loads(content)