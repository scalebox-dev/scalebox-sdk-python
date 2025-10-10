from typing import Dict, List, Literal, Optional, Union, overload

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
from ...generated.rpc import handle_rpc_exception
from ...sandbox.commands.command_handle import CommandResult
from ...sandbox.commands.main import ProcessInfo
from ...sandbox_async.commands.command_handle import AsyncCommandHandle, Stderr, Stdout
from ...sandbox_async.utils import OutputHandler


class Commands:
    """
    Module for executing commands in the sandbox.
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
            http_client=pool
        )
        self._headers=connection_config.headers
        self._pool = pool

    async def list(
        self,
        request_timeout: Optional[float] = None,
    ) -> List[ProcessInfo]:
        """
        Lists all running commands and PTY sessions.

        :param request_timeout: Timeout for the request in **seconds**

        :return: List of running commands and PTY sessions
        """
        try:
            res = await self._rpc.list(
                api_pb2.ListRequest(),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )
            return [
                ProcessInfo(
                    pid=p.pid,
                    tag=p.tag,
                    cmd=p.config.cmd,
                    args=list(p.config.args),
                    envs=dict(p.config.envs),
                    cwd=p.config.cwd,
                )
                for p in res.processes
            ]
        except Exception as e:
            raise handle_rpc_exception(e)

    async def kill(
        self,
        pid: int,
        request_timeout: Optional[float] = None,
    ) -> bool:
        """
        Kill a running command specified by its process ID.
        It uses `SIGKILL` signal to kill the command.

        :param pid: Process ID of the command. You can get the list of processes using `sandbox.commands.list()`
        :param request_timeout: Timeout for the request in **seconds**

        :return: `True` if the command was killed, `False` if the command was not found
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
            if "not found" in str(e):
                return False
            raise handle_rpc_exception(e)

    async def send_stdin(
        self,
        pid: int,
        data: str,
        request_timeout: Optional[float] = None,
    ) -> None:
        """
        Send data to command stdin.

        :param pid Process ID of the command. You can get the list of processes using `sandbox.commands.list()`.
        :param data: Data to send to the command
        :param request_timeout: Timeout for the request in **seconds**
        """
        try:
            await self._rpc.send_input(
                api_pb2.SendInputRequest(
                    process=api_pb2.ProcessSelector(pid=pid),
                    input=api_pb2.ProcessInput(
                        stdin=data.encode(),
                    ),
                ),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )
        except Exception as e:
            print(e)
            raise handle_rpc_exception(e)

    @overload
    async def run(
        self,
        cmd: str,
        background: Union[Literal[False], None] = None,
        envs: Optional[Dict[str, str]] = None,
        user: Username = "user",
        cwd: Optional[str] = None,
        on_stdout: Optional[OutputHandler[Stdout]] = None,
        on_stderr: Optional[OutputHandler[Stderr]] = None,
        timeout: Optional[float] = 60,
        request_timeout: Optional[float] = None,
    ) -> CommandResult:
        """
        Start a new command and wait until it finishes executing.

        :param cmd: Command to execute
        :param background: **`False` if the command should be executed in the foreground**, `True` if the command should be executed in the background
        :param envs: Environment variables used for the command
        :param user: User to run the command as
        :param cwd: Working directory to run the command
        :param on_stdout: Callback for command stdout output
        :param on_stderr: Callback for command stderr output
        :param timeout: Timeout for the command connection in **seconds**. Using `0` will not limit the command connection time
        :param request_timeout: Timeout for the request in **seconds**

        :return: `CommandResult` result of the command execution
        """
        ...

    @overload
    async def run(
        self,
        cmd: str,
        background: Literal[True],
        envs: Optional[Dict[str, str]] = None,
        user: Username = "user",
        cwd: Optional[str] = None,
        on_stdout: Optional[OutputHandler[Stdout]] = None,
        on_stderr: Optional[OutputHandler[Stderr]] = None,
        timeout: Optional[float] = 60,
        request_timeout: Optional[float] = None,
    ) -> AsyncCommandHandle:
        """
        Start a new command and return a handle to interact with it.

        :param cmd: Command to execute
        :param background: `False` if the command should be executed in the foreground, **`True` if the command should be executed in the background**
        :param envs: Environment variables used for the command
        :param user: User to run the command as
        :param cwd: Working directory to run the command
        :param on_stdout: Callback for command stdout output
        :param on_stderr: Callback for command stderr output
        :param timeout: Timeout for the command connection in **seconds**. Using `0` will not limit the command connection time
        :param request_timeout: Timeout for the request in **seconds**

        :return: `AsyncCommandHandle` handle to interact with the running command
        """
        ...

    async def run(
        self,
        cmd: str,
        background: Union[bool, None] = None,
        envs: Optional[Dict[str, str]] = None,
        user: Username = "user",
        cwd: Optional[str] = None,
        on_stdout: Optional[OutputHandler[Stdout]] = None,
        on_stderr: Optional[OutputHandler[Stderr]] = None,
        timeout: Optional[float] = 60,
        request_timeout: Optional[float] = None,
    ):
        proc = await self._start(
            cmd,
            envs,
            user,
            cwd,
            timeout,
            request_timeout,
            on_stdout=on_stdout,
            on_stderr=on_stderr,
        )
        return proc if background else await proc.wait()

    async def _start(
        self,
        cmd: str,
        envs: Optional[Dict[str, str]] = None,
        user: Username = "user",
        cwd: Optional[str] = None,
        timeout: Optional[float] = 60,
        request_timeout: Optional[float] = None,
        on_stdout: Optional[OutputHandler[Stdout]] = None,
        on_stderr: Optional[OutputHandler[Stderr]] = None,
    ) -> AsyncCommandHandle:
        try:
            events = self._rpc.start(
                api_pb2.StartRequest(
                    process=api_pb2.ProcessConfig(
                        cmd="/bin/bash",
                        envs=envs,
                        args=["-l", "-c", cmd],
                        cwd=cwd,
                    ),
                ),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )
            start_event = await events.__anext__()

            if not start_event.HasField("event"):
                raise SandboxException(
                    f"Failed to start process: expected start event, got {start_event}"
                )

            return AsyncCommandHandle(
                pid=start_event.event.start.pid,
                handle_kill=lambda: self.kill(start_event.event.start.pid),
                events=events,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
            )
        except Exception as e:
            raise handle_rpc_exception(e)

    async def connect(
        self,
        pid: int,
        timeout: Optional[float] = 60,
        request_timeout: Optional[float] = None,
        on_stdout: Optional[OutputHandler[Stdout]] = None,
        on_stderr: Optional[OutputHandler[Stderr]] = None,
    ) -> AsyncCommandHandle:
        """
        Connects to a running command.
        You can use `AsyncCommandHandle.wait()` to wait for the command to finish and get execution results.

        :param pid: Process ID of the command to connect to. You can get the list of processes using `sandbox.commands.list()`
        :param request_timeout: Request timeout in **seconds**
        :param timeout: Timeout for the command connection in **seconds**. Using `0` will not limit the command connection time
        :param on_stdout: Callback for command stdout output
        :param on_stderr: Callback for command stderr output

        :return: `AsyncCommandHandle` handle to interact with the running command
        """
        events = self._rpc.connect(
            api_pb2.ConnectRequest(
                process=api_pb2.ProcessSelector(pid=pid),
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
                    f"Failed to connect to process: expected start event, got {start_event}"
                )

            return AsyncCommandHandle(
                pid=start_event.event.start.pid,
                handle_kill=lambda: self.kill(start_event.event.start.pid),
                events=events,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
            )
        except Exception as e:
            raise handle_rpc_exception(e)
