import logging
import socket
import time
from typing import Dict, Iterator, Literal, Optional, Union, overload

import urllib3
from httpx import Timeout
from urllib3 import Retry

from ..exceptions import InvalidArgumentException
from ..generated import api_pb2, api_pb2_connect
from ..sandbox_sync.main import Sandbox as BaseSandbox
from .constants import DEFAULT_TEMPLATE, DEFAULT_TIMEOUT, JUPYTER_PORT
from .exceptions import format_execution_timeout_error, format_request_timeout_error
from .models import (
    Context,
    Execution,
    ExecutionError,
    OutputHandler,
    OutputMessage,
    Result,
    parse_output,
)

logger = logging.getLogger(__name__)


class Sandbox(BaseSandbox):
    """
    E2B cloud sandbox is a secure and isolated cloud environment.

    The sandbox allows you to:
    - Access Linux OS
    - Create, list, and delete files and directories
    - Run commands
    - Run isolated code
    - Access the internet

    Check docs [here](https://.dev/docs).

    Use the `Sandbox()` to create a new sandbox.

    Example:
    ```python
    from scalebox.code_interpreter import Sandbox

    sandbox = Sandbox()
    ```
    """

    default_template = DEFAULT_TEMPLATE

    @property
    def _jupyter_url(self) -> str:
        return f"{'http' if self.connection_config.debug else 'https'}://{self.get_host(JUPYTER_PORT)}"

    @overload
    def run_code(
        self,
        code: str,
        language: Union[Literal["python"], None] = "python",
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
    def run_code(
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
    def run_code(
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

    def run_code(
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

        if language and context:
            raise InvalidArgumentException(
                "You can provide context or language, but not both at the same time."
            )

        timeout = None if timeout == 0 else (timeout or DEFAULT_TIMEOUT)
        request_timeout = request_timeout or self._connection_config.request_timeout
        context_id = context.id if context else None
        client = api_pb2_connect.ExecutionServiceClient(
            base_url=self.envd_api_url,
            http_client=self._urllib3_pool,
        )

        # Create execution request
        execute_request = api_pb2.ExecuteRequest(
            code=code,
            context_id=context_id or "",
            language=language or "",
            env_vars=envs,
        )

        try:
            # Calculate deadline for gRPC call
            deadline = time.time() + request_timeout + (timeout or 0)

            # Execute code via gRPC
            execution = Execution()
            # headers = {
            #     "Authorization": "Bearer root",
            # }
            response_stream = client.execute(
                execute_request,
                timeout_seconds=deadline - time.time(),
                extra_headers=self.connection_config.headers,
            )

            # Process stream responses
            for response in response_stream:
                # Convert gRPC response to the format expected by parse_output
                # This assumes parse_output can handle gRPC response format
                # You might need to adjust parse_output or convert the response here
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
            # Handle different types of timeout exceptions
            if "timeout" in str(e).lower() or "deadline" in str(e).lower():
                if "execution" in str(e).lower():
                    raise format_execution_timeout_error()
                else:
                    raise format_request_timeout_error()
            else:
                # Re-raise other exceptions
                raise e

    def create_code_context(
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

        # Create context request
        create_context_request = api_pb2.CreateContextRequest(
            language=language or "python3",
            cwd=cwd or "",
        )

        try:
            client = api_pb2_connect.ContextServiceClient(
                base_url=self.envd_api_url,
                http_client=self._urllib3_pool,
            )
            # headers = {
            #     "Authorization": "Bearer root",
            # }
            # Create context via gRPC
            response = client.create_context(
                create_context_request,
                timeout_seconds=request_timeout
                or self._connection_config.request_timeout,
                extra_headers=headers,
            )

            return Context.from_json(
                {
                    "id": response.id,
                    "language": response.language,
                    "cwd": response.cwd,
                }
            )

        except Exception as e:
            # Handle timeout exceptions
            if "timeout" in str(e).lower() or "deadline" in str(e).lower():
                raise format_request_timeout_error()
            else:
                # Re-raise other exceptions
                raise e

    def destroy_context(self, context: Context) -> None:
        """
        Destroys a context.

        :param context: Context to destroy
        """
        logger.debug(f"Destroying context {context.id}")

        # Create destroy context request
        destroy_context_request = api_pb2.DestroyContextRequest(
            context_id=context.id,
        )

        try:
            client = api_pb2_connect.ContextServiceClient(
                base_url=self.envd_api_url,
                http_client=self._urllib3_pool,
            )
            # headers = {
            #     "Authorization": "Bearer root",
            # }
            client.destroy_context(destroy_context_request,extra_headers=self.connection_config.headers)

        except Exception as e:
            logger.warning(f"Failed to destroy context {context.id}: {e}")
