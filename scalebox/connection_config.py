import os
from typing import Dict, Literal, Optional

from httpx._types import ProxyTypes

# from .api.metadata import package_version

REQUEST_TIMEOUT: float = 30.0  # 30 seconds

KEEPALIVE_PING_INTERVAL_SEC = 50  # 50 seconds
KEEPALIVE_PING_HEADER = "Keepalive-Ping-Interval"


class ConnectionConfig:
    """
    Configuration for the connection to the API.
    """

    @staticmethod
    def _domain():
        return os.getenv("SBX_DOMAIN") or "api.scalebox.dev/v1"

    @staticmethod
    def _debug():
        return os.getenv("SBX_DEBUG", "false").lower() == "true"

    @staticmethod
    def _api_key():
        return os.getenv("SBX_API_KEY")

    @staticmethod
    def _access_token():
        return os.getenv("SBX_ACCESS_TOKEN")

    def __init__(
        self,
        domain: Optional[str] = None,
        debug: Optional[bool] = None,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        request_timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[ProxyTypes] = None,
    ):
        self.domain = domain or ConnectionConfig._domain()
        self.debug = debug or ConnectionConfig._debug()
        self.api_key = api_key or ConnectionConfig._api_key()
        self.access_token = access_token or ConnectionConfig._access_token()
        self.headers = headers or {}
        # self.headers["User-Agent"] = f"csx-python-sdk/{package_version}"

        self.proxy = proxy

        self.request_timeout = ConnectionConfig._get_request_timeout(
            REQUEST_TIMEOUT,
            request_timeout,
        )

        if request_timeout == 0:
            self.request_timeout = None
        elif request_timeout is not None:
            self.request_timeout = request_timeout
        else:
            self.request_timeout = REQUEST_TIMEOUT

        self.api_url = f"https://{self.domain}"

    @staticmethod
    def _get_request_timeout(
        default_timeout: Optional[float],
        request_timeout: Optional[float],
    ):
        if request_timeout == 0:
            return None
        elif request_timeout is not None:
            return request_timeout
        else:
            return default_timeout

    def get_request_timeout(self, request_timeout: Optional[float] = None):
        return self._get_request_timeout(self.request_timeout, request_timeout)


Username = Literal["root", "user"]
"""
User used for the operation in the sandbox.
"""

default_username: Username = "user"
"""
Default user used for the operation in the sandbox.
"""
