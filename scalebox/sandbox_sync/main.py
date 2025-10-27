import datetime
import logging
import socket
import time
from typing import Dict, List, Optional, TypedDict, overload

import httpx
import urllib3
from httpx import Timeout
from packaging.version import Version
from urllib3 import Retry

from ..api.client.types import Unset
from ..connection_config import ConnectionConfig, ProxyTypes
from ..exceptions import SandboxException, request_timeout_error
from ..generated.api import ENVD_API_HEALTH_ROUTE, handle_envd_api_exception
from ..sandbox.main import SandboxSetup
from ..sandbox.sandbox_api import SandboxMetrics
from ..sandbox.utils import class_method_variant
from ..sandbox_sync.commands.command import Commands
from ..sandbox_sync.commands.pty import Pty
from ..sandbox_sync.filesystem.filesystem import Filesystem
from ..sandbox_sync.sandbox_api import SandboxApi, SandboxInfo

logger = logging.getLogger(__name__)


class TransportWithLogger(httpx.HTTPTransport):
    def handle_request(self, request):
        url = f"{request.url.scheme}://{request.url.host}{request.url.path}"
        logger.info(f"Request: {request.method} {url}")
        response = super().handle_request(request)

        # data = connect.GzipCompressor.decompress(response.read()).decode()
        logger.info(f"Response: {response.status_code} {url}")

        return response

class SandboxOpts(TypedDict):
    sandbox_id: str
    sandbox_domain: Optional[str]
    envd_version: Optional[str]
    envd_access_token: Optional[str]
    connection_config: ConnectionConfig

class Sandbox(SandboxSetup, SandboxApi):
    """
    SBX cloud sandbox is a secure and isolated cloud environment.

    The sandbox allows you to:
    - Access Linux OS
    - Create, list, and delete files and directories
    - Run commands
    - Run isolated code
    - Access the internet

    Check docs [here](https://..dev/docs).

    Use the `Sandbox()` to create a new sandbox.

    Example:
    ```python
    from SBX import Sandbox

    sandbox = Sandbox()
    ```
    """

    @property
    def files(self) -> Filesystem:
        """
        Module for interacting with the sandbox filesystem.
        """
        return self._filesystem

    @property
    def commands(self) -> Commands:
        """
        Module for running commands in the sandbox.
        """
        return self._commands

    @property
    def pty(self) -> Pty:
        """
        Module for interacting with the sandbox pseudo-terminal.
        """
        return self._pty

    @property
    def sandbox_id(self) -> str:
        """
        Unique identifier of the sandbox.
        """
        return self._sandbox_id

    @property
    def sandbox_domain(self) -> str:
        """
        Domain where the sandbox is hosted.
        """
        return self._sandbox_domain

    @property
    def envd_api_url(self) -> str:
        return self._envd_api_url

    @property
    def _envd_access_token(self) -> str:
        """Private property to access the envd token"""
        return self.__envd_access_token

    @_envd_access_token.setter
    def _envd_access_token(self, value: Optional[str]):
        """Private setter for envd token"""
        self.__envd_access_token = value

    @property
    def connection_config(self) -> ConnectionConfig:
        return self._connection_config

    # def __init__(
    #     self,
    #     template: Optional[str] = None,
    #     timeout: Optional[int] = None,
    #     metadata: Optional[Dict[str, str]] = None,
    #     envs: Optional[Dict[str, str]] = None,
    #     secure: Optional[bool] = None,
    #     api_key: Optional[str] = None,
    #     domain: Optional[str] = None,
    #     debug: Optional[bool] = None,
    #     sandbox_id: Optional[str] = None,
    #     request_timeout: Optional[float] = None,
    #     proxy: Optional[ProxyTypes] = None,
    #     allow_internet_access: Optional[bool] = True,
    # ):
    def __init__(self, **opts):
        """
        Create a new sandbox.

        By default, the sandbox is created from the default `base` sandbox template.

        :param template: Sandbox template name or ID
        :param timeout: Timeout for the sandbox in **seconds**, default to 300 seconds. Maximum time a sandbox can be kept alive is 24 hours (86_400 seconds) for Pro users and 1 hour (3_600 seconds) for Hobby users
        :param metadata: Custom metadata for the sandbox
        :param envs: Custom environment variables for the sandbox
        :param api_key: SBX API Key to use for authentication, defaults to `SBX_API_KEY` environment variable
        :param request_timeout: Timeout for the request in **seconds**
        :param proxy: Proxy to use for the request and for the **requests made to the returned sandbox**
        :param allow_internet_access: Allow sandbox to access the internet, defaults to `True`

        :return: sandbox instance for the new sandbox
        """
        super().__init__()
        self._connection_config = opts["connection_config"]

        self._sandbox_id = opts["sandbox_id"]
        self._sandbox_domain = opts["sandbox_domain"] or self.connection_config.domain
        debug = self._connection_config.debug
        # connection_headers = {"Authorization": "Bearer root", }

        # if debug:
        #     self._sandbox_id = "debug_sandbox_id"
        #     self._sandbox_domain = None
        #     self._envd_version = None
        #     self._envd_access_token = None
        # elif sandbox_id is not None:
        #     response = SandboxApi._cls_get_info(
        #         sandbox_id,
        #         api_key=api_key,
        #         domain=domain,
        #         debug=debug,
        #         request_timeout=request_timeout,
        #         proxy=proxy,
        #     )
        #
        #     self._sandbox_id = sandbox_id
        #     self._sandbox_domain = response.sandbox_domain
        #     self._envd_version = response.envd_version
        #     self._envd_access_token = response._envd_access_token
        #
        #     if response._envd_access_token is not None and not isinstance(
        #         response._envd_access_token, Unset
        #     ):
        #         connection_headers["X-Access-Token"] = response._envd_access_token
        # else:
        #     template = template or self.default_template
        #     timeout = timeout or self.default_sandbox_timeout
        #     response = SandboxApi._create_sandbox(
        #         template=template,
        #         api_key=api_key,
        #         timeout=timeout,
        #         metadata=metadata,
        #         env_vars=envs,
        #         domain=domain,
        #         debug=debug,
        #         request_timeout=request_timeout,
        #         secure=secure or False,
        #         proxy=proxy,
        #         allow_internet_access=allow_internet_access,
        #     )
        #
        #     self._sandbox_id = response.sandbox_id
        #     self._sandbox_domain = response.sandbox_domain
        #     self._envd_version = response.envd_version
        #
        #     if response.envd_access_token is not None and not isinstance(
        #         response.envd_access_token, Unset
        #     ):
        #         self._envd_access_token = response.envd_access_token
        #         connection_headers["X-Access-Token"] = response.envd_access_token
        #     else:
        #         self._envd_access_token = None
        # self._transport = TransportWithLogger(limits=self._limits, proxy=proxy)
        # self._connection_config = ConnectionConfig(
        #     api_key=api_key,
        #     domain=domain,
        #     debug=debug,
        #     request_timeout=request_timeout,
        #     headers=connection_headers,
        #     proxy=proxy,
        # )

        self._sandbox_domain = self._sandbox_domain or self._connection_config.domain
        # self._envd_api_url = f"{'http' if self.connection_config.debug else 'https'}://{self.get_host(self.envd_port)}"
        if debug:
            self._envd_api_url = f"http://{self.get_host(8888)}"
        # elif self._sandbox_id is not None:
        #     response = SandboxApi._cls_get_info(
        #         self._sandbox_id,
        #         api_key=self._api_key(),
        #         domain=self._sandbox_domain,
        #         debug=debug,
        #         request_timeout=self.request_timeout,
        #         proxy=self.proxy,
        #     )
        #
        #     self._sandbox_id = self._sandbox_id
        #     self._sandbox_domain = response.sandbox_domain
        #     self._envd_version = response.envd_version
        #     self._envd_access_token = response._envd_access_token
        #
        #     if response._envd_access_token is not None and not isinstance(
        #         response._envd_access_token, Unset
        #     ):
        #         self._connection_config["X-Access-Token"] = response._envd_access_token
        #     self._envd_api_url = f"http://{self.get_host(self.envd_port)}"
        else:
            self._envd_api_url = f"https://{self.get_host(self.envd_port)}"
        self._transport = TransportWithLogger(limits=self._limits, proxy=self._connection_config.proxy)
        # self._envd_api_url = f"http://localhost:8088"
        # self._envd_api_url = f"http://{self.get_host(self.envd_port)}"
        # self._envd_api_url = f"http://localhost:31000"
        self._envd_api = httpx.Client(
            base_url=self._envd_api_url,
            transport=self._transport,
            headers=self.connection_config.headers,
        )

        self._envd_version=f"v1.0"
        # 准备连接池参数
        connection_pool_kw = {
            # 连接池大小
            "maxsize": 100,
            "block": False,
            # 超时设置
            "timeout": self._connection_config.request_timeout,
            # 重试策略
            "retries": Retry(
                total=3,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504]
            ),
            # SSL 设置
            # "cert_reqs": 'CERT_NONE',
            "ca_certs": None,
            # 套接字选项
            "socket_options": [
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
            ],
        }

        # 如果有代理配置，添加到连接池参数
        if hasattr(self._connection_config, 'proxy') and self._connection_config.proxy:
            connection_pool_kw["proxy_url"] = self._connection_config.proxy

        # 创建 urllib3.PoolManager 连接池
        self._urllib3_pool = urllib3.PoolManager(
            num_pools=10,  # 池的数量
            headers=self._connection_config.headers,  # 默认头部
            **connection_pool_kw  # 连接池参数
        )

        self._filesystem = Filesystem(
            self.envd_api_url,
            self._envd_version,
            self.connection_config,
            self._urllib3_pool,
            self._envd_api,
        )
        self._commands = Commands(
            self.envd_api_url,
            self.connection_config,
            self._urllib3_pool,
        )
        self._pty = Pty(
            self.envd_api_url,
            self.connection_config,
            self._urllib3_pool,
        )

    @classmethod
    def create(
            cls,
            template: Optional[str] = None,
            timeout: Optional[int] = None,
            metadata: Optional[Dict[str, str]] = None,
            envs: Optional[Dict[str, str]] = None,
            api_key: Optional[str] = None,
            domain: Optional[str] = None,
            debug: Optional[bool] = None,
            sandbox_id: Optional[str] = None,
            request_timeout: Optional[float] = None,
            proxy: Optional[ProxyTypes] = None,
            secure: Optional[bool] = None,
            allow_internet_access: Optional[bool] = True,
    ):
        """
        Create a new sandbox.

        By default, the sandbox is created from the default `base` sandbox template.

        :param template: Sandbox template name or ID
        :param timeout: Timeout for the sandbox in **seconds**, default to 300 seconds. Maximum time a sandbox can be kept alive is 24 hours (86_400 seconds) for Pro users and 1 hour (3_600 seconds) for Hobby users.
        :param metadata: Custom metadata for the sandbox
        :param envs: Custom environment variables for the sandbox
        :param api_key: scalebox API Key to use for authentication, defaults to `CSX_API_KEY` environment variable
        :param request_timeout: Timeout for the request in **seconds**
        :param proxy: Proxy to use for the request and for the **requests made to the returned sandbox**
        :param secure: Envd is secured with access token and cannot be used without it
        :param allow_internet_access: Allow sandbox to access the internet, defaults to `True`.

        :return: sandbox instance for the new sandbox

        Use this method instead of using the constructor to create a new sandbox.
        """
        if sandbox_id and (metadata is not None or template is not None):
            raise SandboxException(
                "Cannot set metadata or timeout when connecting to an existing sandbox. "
                "Use Sandbox.connect method instead.",
            )
        connection_headers = {"Authorization": "Bearer root", }
        if debug:
            sandbox_id = "debug_sandbox_id"
            sandbox_domain = None
            envd_version = None
            envd_access_token = "123456789"
        elif sandbox_id is not None:
            response = SandboxApi._cls_get_info(
                sandbox_id,
                api_key=api_key,
                domain=domain,
                debug=debug,
                request_timeout=request_timeout,
                proxy=proxy,
            )

            sandbox_domain = response.sandbox_domain
            envd_version = response.envd_version
            envd_access_token = response._envd_access_token

            if response._envd_access_token is not None and not isinstance(
                    response._envd_access_token, Unset
            ):
                connection_headers["X-Access-Token"] = response._envd_access_token
        else:
            response = SandboxApi._create_sandbox(
                template=template or cls.default_template,
                api_key=api_key,
                timeout=timeout or cls.default_sandbox_timeout,
                metadata=metadata,
                domain=domain,
                debug=debug,
                request_timeout=request_timeout,
                env_vars=envs,
                secure=secure,
                proxy=proxy,
                allow_internet_access=allow_internet_access,
            )

            sandbox_id = response.sandbox_id
            sandbox_domain = response.sandbox_domain
            envd_version = response.envd_version
            envd_access_token = response.envd_access_token

        if envd_access_token is not None and not isinstance(
                envd_access_token, Unset
        ):
            connection_headers["X-Access-Token"] = envd_access_token

        connection_config = ConnectionConfig(
            api_key=api_key,
            domain=domain,
            debug=debug,
            request_timeout=request_timeout,
            headers=connection_headers,
            proxy=proxy,
        )
        print("connection_config" + str(connection_config.__dict__))
        sanbox= cls(
            sandbox_id=sandbox_id,
            sandbox_domain=sandbox_domain,
            envd_version=envd_version,
            envd_access_token=envd_access_token,
            connection_config=connection_config,
        )

        timeout = 5.0
        interval = 0.3
        elapsed = 0.0
        while elapsed <= timeout:
            try:
                isRunning = sanbox.is_running(request_timeout=1)
                if isRunning:
                    break
            except Exception:
                pass
            time.sleep(interval)
            elapsed += interval
        else:
            print("connect "+sandbox_domain+ENVD_API_HEALTH_ROUTE +" timeout 5s")
        return sanbox

    def is_running(self, request_timeout: Optional[float] = None) -> bool:
        """
        Check if the sandbox is running.

        :param request_timeout: Timeout for the request in **seconds**

        :return: `True` if the sandbox is running, `False` otherwise

        Example
        ```python
        sandbox = Sandbox()
        sandbox.is_running() # Returns True

        sandbox.kill()
        sandbox.is_running() # Returns False
        ```
        """
        try:
            r = self._envd_api.get(
                ENVD_API_HEALTH_ROUTE,
                timeout=self.connection_config.get_request_timeout(request_timeout),
            )
            print(r)
            if r.status_code == 502:
                return False

            err = handle_envd_api_exception(r)

            if err:
                raise err

        except httpx.TimeoutException:
            raise request_timeout_error()

        return True

    @classmethod
    def connect(
        cls,
        sandbox_id: str,
        api_key: Optional[str] = None,
        domain: Optional[str] = None,
        debug: Optional[bool] = None,
        proxy: Optional[ProxyTypes] = None,
    ):
        """
        Connects to an existing Sandbox.
        With sandbox ID you can connect to the same sandbox from different places or environments (serverless functions, etc).

        :param sandbox_id: Sandbox ID
        :param api_key: Scalebox API Key to use for authentication, defaults to `SBX_API_KEY` environment variable
        :param proxy: Proxy to use for the request and for the **requests made to the returned sandbox**

        :return: sandbox instance for the existing sandbox

        @example
        ```python
        sandbox = Sandbox()
        sandbox_id = sandbox.sandbox_id

        # Another code block
        same_sandbox = Sandbox.connect(sandbox_id)
        ```
        """
        connection_headers = {"Authorization": "Bearer root"}

        response = SandboxApi._cls_get_info(
            sandbox_id,
            api_key=api_key,
            domain=domain,
            debug=debug,
            proxy=proxy,
        )

        if response._envd_access_token is not None and not isinstance(
            response._envd_access_token, Unset
        ):
            connection_headers["X-Access-Token"] = response._envd_access_token
        connection_config = ConnectionConfig(
            api_key=api_key,
            domain=domain,
            debug=debug,
            headers=connection_headers,
            proxy=proxy,
        )

        return cls(
            sandbox_id=sandbox_id,
            sandbox_domain=response.sandbox_domain,
            envd_version=response.envd_version,
            envd_access_token=response._envd_access_token,
            connection_config=connection_config,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.kill()

    @overload
    def kill(self, request_timeout: Optional[float] = None) -> bool:
        """
        Kill the sandbox.

        :param request_timeout: Timeout for the request in **seconds**

        :return: `True` if the sandbox was killed, `False` if the sandbox was not found
        """
        ...

    @overload
    @staticmethod
    def kill(
        sandbox_id: str,
        api_key: Optional[str] = None,
        domain: Optional[str] = None,
        debug: Optional[bool] = None,
        request_timeout: Optional[float] = None,
        proxy: Optional[ProxyTypes] = None,
    ) -> bool:
        """
        Kill the sandbox specified by sandbox ID.

        :param sandbox_id: Sandbox ID
        :param api_key: SBX API Key to use for authentication, defaults to `SBX_API_KEY` environment variable
        :param request_timeout: Timeout for the request in **seconds**
        :param proxy: Proxy to use for the request

        :return: `True` if the sandbox was killed, `False` if the sandbox was not found
        """
        ...

    @class_method_variant("_cls_kill")
    def kill(self, request_timeout: Optional[float] = None) -> bool:  # type: ignore
        """
        Kill the sandbox.

        :param request_timeout: Timeout for the request
        :return: `True` if the sandbox was killed, `False` if the sandbox was not found
        """
        config_dict = self.connection_config.__dict__
        config_dict.pop("access_token", None)
        config_dict.pop("api_url", None)

        if request_timeout:
            config_dict["request_timeout"] = request_timeout

        SandboxApi._cls_kill(
            sandbox_id=self.sandbox_id,
            **config_dict,
        )

    @overload
    def set_timeout(
        self,
        timeout: int,
        request_timeout: Optional[float] = None,
    ) -> None:
        """
        Set the timeout of the sandbox.
        After the timeout expires the sandbox will be automatically killed.
        This method can extend or reduce the sandbox timeout set when creating the sandbox or from the last call to `.set_timeout`.

        Maximum time a sandbox can be kept alive is 24 hours (86_400 seconds) for Pro users and 1 hour (3_600 seconds) for Hobby users.

        :param timeout: Timeout for the sandbox in **seconds**
        :param request_timeout: Timeout for the request in **seconds**
        """
        ...

    @overload
    @staticmethod
    def set_timeout(
        sandbox_id: str,
        timeout: int,
        api_key: Optional[str] = None,
        domain: Optional[str] = None,
        debug: Optional[bool] = None,
        request_timeout: Optional[float] = None,
        proxy: Optional[ProxyTypes] = None,
    ) -> None:
        """
        Set the timeout of the sandbox specified by sandbox ID.
        After the timeout expires the sandbox will be automatically killed.
        This method can extend or reduce the sandbox timeout set when creating the sandbox or from the last call to `.set_timeout`.

        Maximum time a sandbox can be kept alive is 24 hours (86_400 seconds) for Pro users and 1 hour (3_600 seconds) for Hobby users.

        :param sandbox_id: Sandbox ID
        :param timeout: Timeout for the sandbox in **seconds**
        :param api_key: SBX API Key to use for authentication, defaults to `SBX_API_KEY` environment variable
        :param request_timeout: Timeout for the request in **seconds**
        :param proxy: Proxy to use for the request
        """
        ...

    @class_method_variant("_cls_set_timeout")
    def set_timeout(  # type: ignore
        self,
        timeout: int,
        request_timeout: Optional[float] = None,
    ) -> None:
        config_dict = self.connection_config.__dict__
        config_dict.pop("access_token", None)
        config_dict.pop("api_url", None)

        if request_timeout:
            config_dict["request_timeout"] = request_timeout

        SandboxApi._cls_set_timeout(
            sandbox_id=self.sandbox_id,
            timeout=timeout,
            **config_dict,
        )

    @overload
    def get_info(
        self,
        request_timeout: Optional[float] = None,
    ) -> SandboxInfo:
        """
        Get sandbox information like sandbox ID, template, metadata, started at/end at date.
        :param request_timeout: Timeout for the request in **seconds**
        :return: Sandbox info
        """
        ...

    @overload
    @staticmethod
    def get_info(
        sandbox_id: str,
        api_key: Optional[str] = None,
        domain: Optional[str] = None,
        debug: Optional[bool] = None,
        request_timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[ProxyTypes] = None,
    ) -> SandboxInfo:
        """
        Get sandbox information like sandbox ID, template, metadata, started at/end at date.
        :param sandbox_id: Sandbox ID
        :param api_key: SBX API Key to use for authentication, defaults to `SBX_API_KEY` environment variable
        :param domain: SBX domain to use for authentication, defaults to `SBX_DOMAIN` environment variable
        :param debug: Whether to use debug mode, defaults to `SBX_DEBUG` environment variable
        :param request_timeout: Timeout for the request in **seconds**
        :param headers: Custom headers to use for the request
        :param proxy: Proxy to use for the request
        :return: Sandbox info
        """
        ...

    @class_method_variant("_cls_get_info")
    def get_info(  # type: ignore
        self,
        request_timeout: Optional[float] = None,
    ) -> SandboxInfo:
        """
        Get sandbox information like sandbox ID, template, metadata, started at/end at date.
        :param request_timeout: Timeout for the request in **seconds**
        :return: Sandbox info
        """
        config_dict = self.connection_config.__dict__
        config_dict.pop("access_token", None)
        config_dict.pop("api_url", None)

        if request_timeout:
            config_dict["request_timeout"] = request_timeout

        return SandboxApi._cls_get_info(
            sandbox_id=self.sandbox_id,
            **config_dict,
        )

    @overload
    def get_metrics(  # type: ignore
        self,
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        request_timeout: Optional[float] = None,
    ) -> List[SandboxMetrics]:
        """
        Get the metrics of the current sandbox.

        :param start: Start time for the metrics, defaults to the start of the sandbox
        :param end: End time for the metrics, defaults to current time
        :param request_timeout: Timeout for the request in **seconds**

        :return: List of sandbox metrics containing CPU, memory and disk usage information
        """
        ...

    @overload
    @staticmethod
    def get_metrics(
        sandbox_id: str,
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        api_key: Optional[str] = None,
        domain: Optional[str] = None,
        debug: Optional[bool] = None,
        request_timeout: Optional[float] = None,
    ) -> List[SandboxMetrics]:
        """
        Get the metrics of the sandbox specified by sandbox ID.

        :param sandbox_id: Sandbox ID
        :param start: Start time for the metrics, defaults to the start of the sandbox
        :param end: End time for the metrics, defaults to current time
        :param api_key: SBX API Key to use for authentication, defaults to `SBX_API_KEY` environment variable
        :param request_timeout: Timeout for the request in **seconds**

        :return: List of sandbox metrics containing CPU, memory and disk usage information
        """
        ...

    @class_method_variant("_cls_get_metrics")
    def get_metrics(  # type: ignore
        self,
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        request_timeout: Optional[float] = None,
    ) -> List[SandboxMetrics]:
        """
        Get the metrics of the current sandbox.

        :param start: Start time for the metrics, defaults to the start of the sandbox
        :param end: End time for the metrics, defaults to current time
        :param request_timeout: Timeout for the request in **seconds**

        :return: List of sandbox metrics containing CPU, memory and disk usage information
        """
        if self._envd_version:
            if Version(self._envd_version) < Version("0.1.5"):
                raise SandboxException(
                    "Metrics are not supported in this version of the sandbox, please rebuild your template."
                )

            if Version(self._envd_version) < Version("0.2.4"):
                logger.warning(
                    "Disk metrics are not supported in this version of the sandbox, please rebuild the template to get disk metrics."
                )

        config_dict = self.connection_config.__dict__
        config_dict.pop("access_token", None)
        config_dict.pop("api_url", None)
        if request_timeout:
            config_dict["request_timeout"] = request_timeout

        return self._cls_get_metrics(
            sandbox_id=self.sandbox_id,
            start=start,
            end=end,
            **config_dict,
        )
