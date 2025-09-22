import logging

import aiohttp
import httpx

from typing import Optional, Dict, overload, Union, Literal

from aiohttp import TCPConnector
from httpx import AsyncClient

from ..generated import api_pb2_connect, api_pb2
from ..sandbox_async.main import (
    AsyncSandbox as BaseAsyncSandbox,
)
from ..exceptions import InvalidArgumentException
from ..connection_config import ConnectionConfig

from .constants import (
    DEFAULT_TEMPLATE,
    JUPYTER_PORT,
    DEFAULT_TIMEOUT,
)
from .models import (
    Execution,
    ExecutionError,
    Context,
    Result,
    aextract_exception,
    parse_output,
    OutputHandler,
    OutputMessage,
)
from .exceptions import (
    format_execution_timeout_error,
    format_request_timeout_error,
)

logger = logging.getLogger(__name__)


class AsyncSandbox(BaseAsyncSandbox):
    """
    E2B cloud sandbox is a secure and isolated cloud environment.

    The sandbox allows you to:
    - Access Linux OS
    - Create, list, and delete files and directories
    - Run commands
    - Run isolated code
    - Access the internet

    Check docs [here](https://e2b.dev/docs).

    Use the `AsyncSandbox.create()` to create a new sandbox.

    Example:
    ```python
    from e2b_code_interpreter import AsyncSandbox
    sandbox = await AsyncSandbox.create()
    ```
    """

    default_template = DEFAULT_TEMPLATE

    @property
    def _jupyter_url(self) -> str:
        return f"{'http' if self.connection_config.debug else 'https'}://{self.get_host(JUPYTER_PORT)}"

    @property
    def _client(self) -> AsyncClient:
        return AsyncClient(transport=self._transport)

    @overload
    async def run_code(
        self,
        code: str,
        language: Union[Literal["python"], None] = None,
        on_stdout: Optional[OutputHandler[OutputMessage]] = None,
        on_stderr: Optional[OutputHandler[OutputMessage]] = None,
        on_result: Optional[OutputHandler[Result]] = None,
        on_error: Optional[OutputHandler[ExecutionError]] = None,
        envs: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        request_timeout: Optional[float] = None,
    ) -> Execution:
        """
        Runs the code as Python.

        Specify the `language` or `context` option to run the code as a different language or in a different `Context`.

        You can reference previously defined variables, imports, and functions in the code.

        :param code: Code to execute
        :param language: Language to use for code execution. If not defined, the default Python context is used.
        :param on_stdout: Callback for stdout messages
        :param on_stderr: Callback for stderr messages
        :param on_result: Callback for the `Result` object
        :param on_error: Callback for the `ExecutionError` object
        :param envs: Custom environment variables
        :param timeout: Timeout for the code execution in **seconds**
        :param request_timeout: Timeout for the request in **seconds**

        :return: `Execution` result object
        """
        ...

    @overload
    async def run_code(
        self,
        code: str,
        language: Optional[str] = "python",
        on_stdout: Optional[OutputHandler[OutputMessage]] = None,
        on_stderr: Optional[OutputHandler[OutputMessage]] = None,
        on_result: Optional[OutputHandler[Result]] = None,
        on_error: Optional[OutputHandler[ExecutionError]] = None,
        envs: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        request_timeout: Optional[float] = None,
    ) -> Execution:
        """
        Runs the code for the specified language.

        Specify the `language` or `context` option to run the code as a different language or in a different `Context`.
        If no language is specified, Python is used.

        You can reference previously defined variables, imports, and functions in the code.

        :param code: Code to execute
        :param language: Language to use for code execution. If not defined, the default Python context is used.
        :param on_stdout: Callback for stdout messages
        :param on_stderr: Callback for stderr messages
        :param on_result: Callback for the `Result` object
        :param on_error: Callback for the `ExecutionError` object
        :param envs: Custom environment variables
        :param timeout: Timeout for the code execution in **seconds**
        :param request_timeout: Timeout for the request in **seconds**

        :return: `Execution` result object
        """
        ...

    @overload
    async def run_code(
        self,
        code: str,
        context: Optional[Context] = None,
        on_stdout: Optional[OutputHandler[OutputMessage]] = None,
        on_stderr: Optional[OutputHandler[OutputMessage]] = None,
        on_result: Optional[OutputHandler[Result]] = None,
        on_error: Optional[OutputHandler[ExecutionError]] = None,
        envs: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        request_timeout: Optional[float] = None,
    ) -> Execution:
        """
        Runs the code in the specified context, if not specified, the default context is used.

        Specify the `language` or `context` option to run the code as a different language or in a different `Context`.

        You can reference previously defined variables, imports, and functions in the code.

        :param code: Code to execute
        :param context: Concrete context to run the code in. If not specified, the default context for the language is used. It's mutually exclusive with the language.
        :param on_stdout: Callback for stdout messages
        :param on_stderr: Callback for stderr messages
        :param on_result: Callback for the `Result` object
        :param on_error: Callback for the `ExecutionError` object
        :param envs: Custom environment variables
        :param timeout: Timeout for the code execution in **seconds**
        :param request_timeout: Timeout for the request in **seconds**

        :return: `Execution` result object
        """
        ...

    async def run_code(
        self,
        code: str,
        language: Optional[str] = None,
        context: Optional[Context] = None,
        on_stdout: Optional[OutputHandler[OutputMessage]] = None,
        on_stderr: Optional[OutputHandler[OutputMessage]] = None,
        on_result: Optional[OutputHandler[Result]] = None,
        on_error: Optional[OutputHandler[ExecutionError]] = None,
        envs: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        request_timeout: Optional[float] = None,
    ) -> Execution:
        logger.debug(f"Executing code {code}")

        """
            Execute code in the sandbox and return the execution result.
            """
        logger.debug(f"Executing code: {code}")

        if context and language:
            raise Exception(
                "You can provide context or language, but not both at the same time."
            )

        # timeout = None if timeout == 0 else (timeout or 30)
        request_timeout = request_timeout or self._connection_config.request_timeout
        context_id = context.id if context else None

        # Ensure session exists
        if not self._session or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
                ssl=False
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=request_timeout)
            )

        # Set headers
        headers = {
            "Authorization": "Bearer root",
        }

        try:
            # Create client and execute request
            client = api_pb2_connect.AsyncExecutionServiceClient(
                http_client=self._session,
                base_url=self.envd_api_url,
            )

            # Build request
            request = api_pb2.ExecuteRequest(
                code=code,
                language=language or "",
                context_id=context_id or "",
                env_vars=envs or {}
            )

            # Execute request and get response stream
            responses = client.execute(
                req=request,
                extra_headers=headers,
                timeout_seconds=request_timeout,
            )

            execution = Execution()

            # Process response stream
            async for response in responses:
                parse_output(
                    execution,
                    response,
                    on_stdout=on_stdout,
                    on_stderr=on_stderr,
                    on_result=on_result,
                    on_error=on_error,
                )

            return execution

        except Exception as e:
            # Handle exception
            logger.error(f"Error executing code: {e}")
            raise
        finally:
            # Don't close session here, let context manager handle it
            pass

    async def create_code_context(
        self,
        cwd: Optional[str] = None,
        language: Optional[str] = None,
        request_timeout: Optional[float] = None,
    ) -> Context:
        """
        Creates a new context to run code in.

        :param cwd: Set the current working directory for the context, defaults to `/home/user`
        :param language: Language of the context. If not specified, defaults to Python
        :param request_timeout: Timeout for the request in **milliseconds**

        :return: Context object
        """
        logger.debug(f"Creating new {language} context")

        request_timeout = request_timeout or self._connection_config.request_timeout

        # Ensure session exists
        if not self._session or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
                ssl=False
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=request_timeout)
            )

        data = {}
        if language:
            data["language"] = language
        if cwd:
            data["cwd"] = cwd

        try:
            client = api_pb2_connect.AsyncContextServiceClient(
                http_client=self._session,
                base_url=self.envd_api_url,
            )
            headers = {
                "Authorization": "Bearer root",
            }

            # Build request
            request = api_pb2.CreateContextRequest(
                language=language or "",
                cwd=cwd or "",
            )

            # Execute request and get response stream
            response = await client.create_context(
                req=request,
                extra_headers=headers,
            )
            return Context.from_json(
                {
                    "id":response.id,
                    "language":response.language,
                    "cwd":response.cwd,
                }
            )
        except Exception as e:
            logger.error(f"Error create_code_context: {e}")
            raise e
        finally:
            # Don't close session here, let context manager handle it
            pass

    async def destroy_context(self, context: Context) -> None:
        """
        Destroys a context.

        :param context: Context to destroy
        """
        logger.debug(f"Destroying context {context.id}")

        request_timeout = self._connection_config.request_timeout

        # Ensure session exists
        if not self._session or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
                ssl=False
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=request_timeout)
            )

        # Create destroy context request
        destroy_context_request = api_pb2.DestroyContextRequest(
            context_id=context.id,
        )

        try:
            client = api_pb2_connect.AsyncContextServiceClient(
                base_url=self.envd_api_url,
                http_client=self._session,
            )
            headers = {
                "Authorization": "Bearer root",
            }
            await client.destroy_context(destroy_context_request,extra_headers=headers)
        except Exception as e:
            logger.warning(f"Failed to destroy context {context.id}: {e}")