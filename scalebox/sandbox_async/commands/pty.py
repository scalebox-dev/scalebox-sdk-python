from typing import Dict, Optional

import aiohttp

from ... import csx_connect
from ...connection_config import (
    KEEPALIVE_PING_HEADER,
    KEEPALIVE_PING_INTERVAL_SEC,
    ConnectionConfig,
    Username,
)
from ...exceptions import SandboxException
from ...generated import api_pb2, api_pb2_connect
from ...generated.rpc import authentication_header, handle_rpc_exception
from ...sandbox.commands.command_handle import PtySize
from ...sandbox_async.commands.command_handle import (
    AsyncCommandHandle,
    OutputHandler,
    PtyOutput,
)


class Pty:
    """
    Module for interacting with PTYs (pseudo-terminals) in the sandbox.
    """

    def __init__(
        self,
        envd_api_url: str,
        connection_config: ConnectionConfig,
        pool: aiohttp.ClientSession,
    ) -> None:
        self._connection_config = connection_config
        self._rpc = api_pb2_connect.AsyncProcessClient(
            envd_api_url,
            pool
        )
        self._headers = connection_config.headers
        self._pool = pool

    async def kill(
        self,
        pid: int,
        request_timeout: Optional[float] = None,
    ) -> bool:
        """
        Kill PTY.

        :param pid: Process ID of the PTY
        :param request_timeout: Timeout for the request in **seconds**

        :return: `true` if the PTY was killed, `false` if the PTY was not found
        """
        try:
            await self._rpc.send_signal(
                api_pb2.SendSignalRequest(
                    process=api_pb2.ProcessSelector(pid=pid),
                    signal=api_pb2.Signal.SIGNAL_SIGKILL,
                ),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )
            return True
        except Exception as e:
            if isinstance(e, csx_connect.ConnectException):
                if e.status == csx_connect.Code.not_found:
                    return False
            raise handle_rpc_exception(e)

    async def send_stdin(
        self,
        pid: int,
        data: bytes,
        request_timeout: Optional[float] = None,
    ) -> None:
        """
        Send input to a PTY.

        :param pid: Process ID of the PTY
        :param data: Input data to send
        :param request_timeout: Timeout for the request in **seconds**
        """
        try:
            await self._rpc.send_input(
                api_pb2.SendInputRequest(
                    process=api_pb2.ProcessSelector(pid=pid),
                    input=api_pb2.ProcessInput(
                        pty=data,
                    ),
                ),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )
        except Exception as e:
            raise handle_rpc_exception(e)

    async def create(
        self,
        size: PtySize,
        on_data: OutputHandler[PtyOutput],
        user: Username = "user",
        cwd: Optional[str] = None,
        envs: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = 60,
        request_timeout: Optional[float] = None,
    ) -> AsyncCommandHandle:
        """
        Start a new PTY (pseudo-terminal).

        :param size: Size of the PTY
        :param on_data: Callback to handle PTY data
        :param user: User to use for the PTY
        :param cwd: Working directory for the PTY
        :param envs: Environment variables for the PTY
        :param timeout: Timeout for the PTY in **seconds**
        :param request_timeout: Timeout for the request in **seconds**

        :return: Handle to interact with the PTY
        """
        envs = envs or {}
        envs["TERM"] = "xterm-256color"
        events = self._rpc.start(
            api_pb2.StartRequest(
                process=api_pb2.ProcessConfig(
                    cmd="/bin/bash",
                    envs=envs,
                    args=["-i", "-l"],
                    cwd=cwd,
                ),
                pty=api_pb2.PTY(
                    size=api_pb2.PTY.Size(rows=size.rows, cols=size.cols)
                ),
            ),
            self._headers,
            timeout_seconds=self._connection_config.get_request_timeout(
                request_timeout
            ),
        )

        try:
            start_event = await events.__anext__()

            if not start_event.HasField("event"):
                raise SandboxException(
                    f"Failed to start process: expected start event, got {start_event}"
                )

            return AsyncCommandHandle(
                pid=start_event.event.start.pid,
                handle_kill=lambda: self.kill(start_event.event.start.pid),
                events=events,
                on_pty=on_data,
            )
        except Exception as e:
            raise handle_rpc_exception(e)

    async def resize(
        self,
        pid: int,
        size: PtySize,
        request_timeout: Optional[float] = None,
    ):
        """
        Resize PTY.
        Call this when the terminal window is resized and the number of columns and rows has changed.

        :param pid: Process ID of the PTY
        :param size: New size of the PTY
        :param request_timeout: Timeout for the request in **seconds**
        """
        await self._rpc.update(
            api_pb2.UpdateRequest(
                process=api_pb2.ProcessSelector(pid=pid),
                pty=api_pb2.PTY(
                    size=api_pb2.PTY.Size(rows=size.rows, cols=size.cols),
                ),
            ),
            self._headers,
            timeout_seconds=self._connection_config.get_request_timeout(
                request_timeout
            ),
        )
