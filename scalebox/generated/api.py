import json

import httpx

from ..exceptions import (
    AuthenticationException,
    InvalidArgumentException,
    NotEnoughSpaceException,
    NotFoundException,
    SandboxException,
    sandbox_timeout_exception,
)

ENVD_API_UPLOAD_FILES_ROUTE = "/upload"
ENVD_API_DOWNLOAD_FILES_ROUTE = "/download"
ENVD_API_FILES_ROUTE = "/files"
ENVD_API_HEALTH_ROUTE = "/health"


def get_message(e: httpx.Response) -> str:
    try:
        message = e.json().get("message", e.text)
    except json.JSONDecodeError:
        message = e.text

    return message


def handle_envd_api_exception(res: httpx.Response):
    if res.is_success:
        return

    res.read()

    return format_envd_api_exception(res.status_code, get_message(res))


async def ahandle_envd_api_exception(res: httpx.Response):
    if res.is_success:
        return

    await res.aread()

    return format_envd_api_exception(res.status_code, get_message(res))


def format_envd_api_exception(status_code: int, message: str):
    if status_code == 400:
        return InvalidArgumentException(message)
    elif status_code == 401:
        return AuthenticationException(message)
    elif status_code == 404:
        return NotFoundException(message)
    elif status_code == 429:
        return SandboxException(f"{message}: The requests are being rate limited.")
    elif status_code == 502:
        return sandbox_timeout_exception(message)
    elif status_code == 507:
        return NotEnoughSpaceException(message)
    else:
        return SandboxException(f"{status_code}: {message}")
