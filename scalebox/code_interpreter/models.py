import json
import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import (
    List,
    Optional,
    Iterable,
    Dict,
    TypeVar,
    Callable,
    Awaitable,
    Any,
    Union,
)

from httpx import Response
from google.protobuf.timestamp_pb2 import Timestamp

from ..generated import api_pb2
from ..exceptions import NotFoundException, TimeoutException, SandboxException

T = TypeVar("T")
OutputHandler = Union[
    Callable[[T], Any],
    Callable[[T], Awaitable[Any]],
]

logger = logging.getLogger(__name__)


@dataclass
class OutputMessage:
    """
    Represents an output message from the sandbox code execution.
    """

    content: str
    """
    The output content.
    """
    timestamp: int
    """
    Unix epoch in nanoseconds
    """
    error: bool = False
    """
    Whether the output is an error.
    """

    def __str__(self):
        return self.content


@dataclass
class ExecutionError:
    """
    Represents an error that occurred during the execution of a cell.
    """

    name: str
    """
    Name of the error.
    """
    value: str
    """
    Value of the error.
    """
    traceback: str
    """
    The raw traceback of the error.
    """

    def __init__(self, name: str, value: str, traceback: str, **kwargs):
        self.name = name
        self.value = value
        self.traceback = traceback

    def to_json(self) -> str:
        """
        Returns the JSON representation of the Error object.
        """
        data = {"name": self.name, "value": self.value, "traceback": self.traceback}
        return json.dumps(data)


class MIMEType(str):
    """
    Represents a MIME type.
    """


@dataclass
class Result:
    """
    Represents the result of code execution.
    """

    exit_code: int = 0
    """Process exit code."""
    started_at: Optional[datetime] = None
    """Start time."""
    finished_at: Optional[datetime] = None
    """End time."""
    text: Optional[str] = None
    """Text representation."""
    html: Optional[str] = None
    """HTML representation."""
    markdown: Optional[str] = None
    """Markdown representation."""
    svg: Optional[str] = None
    """SVG representation."""
    png: Optional[str] = None
    """PNG representation."""
    jpeg: Optional[str] = None
    """JPEG representation."""
    pdf: Optional[str] = None
    """PDF representation."""
    latex: Optional[str] = None
    """LaTeX representation."""
    json_data: Optional[dict] = None
    """JSON data."""
    javascript: Optional[str] = None
    """JavaScript representation."""
    data: Optional[dict] = None
    """Raw data."""
    chart: Optional[api_pb2.Chart] = None
    """Chart data."""
    execution_count: Optional[int] = None
    """Execution count."""
    is_main_result: bool = False
    """Whether this is the main result."""
    extra: Optional[dict] = None
    """Extra data."""

    def __init__(
        self,
        exit_code: int = 0,
        started_at: Optional[Timestamp] = None,
        finished_at: Optional[Timestamp] = None,
        text: Optional[str] = None,
        html: Optional[str] = None,
        markdown: Optional[str] = None,
        svg: Optional[str] = None,
        png: Optional[str] = None,
        jpeg: Optional[str] = None,
        pdf: Optional[str] = None,
        latex: Optional[str] = None,
        json: Optional[str] = None,
        javascript: Optional[str] = None,
        data: Optional[str] = None,
        chart: Optional[api_pb2.Chart] = None,
        execution_count: Optional[int] = None,
        is_main_result: bool = False,
        extra: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        self.exit_code = exit_code
        self.started_at = self._convert_timestamp(started_at) if started_at else None
        self.finished_at = self._convert_timestamp(finished_at) if finished_at else None
        self.text = text
        self.html = html
        self.markdown = markdown
        self.svg = svg
        self.png = png
        self.jpeg = jpeg
        self.pdf = pdf
        self.latex = latex
        self.json_data = json.loads(json) if json else None
        self.javascript = javascript
        self.data = json.loads(data) if data else None
        self.chart = chart
        self.execution_count = execution_count
        self.is_main_result = is_main_result
        self.extra = dict(extra) if extra else {}

    def _convert_timestamp(self, timestamp: Timestamp) -> datetime:
        """Convert protobuf timestamp to datetime."""
        return datetime.fromtimestamp(timestamp.seconds + timestamp.nanos / 1e9)

    def formats(self) -> Iterable[str]:
        """
        Returns all available formats of the result.

        :return: All available formats of the result.
        """
        formats = []
        if self.text:
            formats.append("text")
        if self.html:
            formats.append("html")
        if self.markdown:
            formats.append("markdown")
        if self.svg:
            formats.append("svg")
        if self.png:
            formats.append("png")
        if self.jpeg:
            formats.append("jpeg")
        if self.pdf:
            formats.append("pdf")
        if self.latex:
            formats.append("latex")
        if self.json_data:
            formats.append("json")
        if self.javascript:
            formats.append("javascript")
        if self.data:
            formats.append("data")
        if self.chart:
            formats.append("chart")

        if self.extra:
            for key in self.extra:
                formats.append(key)

        return formats

    def __str__(self) -> str:
        """
        Returns the text representation of the data.

        :return: The text representation of the data.
        """
        if self.text:
            return f"Result(exit_code={self.exit_code}, text={self.text})"
        else:
            return f"Result(exit_code={self.exit_code}, formats={list(self.formats())})"


@dataclass
class Logs:
    """
    Data printed to stdout and stderr during execution.
    """

    stdout: List[str]
    """List of strings printed to stdout."""
    stderr: List[str]
    """List of strings printed to stderr."""

    def __init__(self, stdout: List[str] = None, stderr: List[str] = None, **kwargs):
        self.stdout = stdout or []
        self.stderr = stderr or []

    def __repr__(self):
        return f"Logs(stdout={self.stdout}, stderr={self.stderr})"

    def to_json(self) -> str:
        """
        Returns the JSON representation of the Logs object.
        """
        data = {"stdout": self.stdout, "stderr": self.stderr}
        return json.dumps(data)


@dataclass
class Execution:
    """
    Represents the result of a code execution.
    """

    results: List[Result]
    """List of execution results."""
    logs: Logs
    """Logs printed during execution."""
    error: Optional[ExecutionError]
    """Error object if an error occurred."""
    execution_count: Optional[int]
    """Execution count."""

    def __init__(
        self,
        results: List[Result] = None,
        logs: Logs = None,
        error: Optional[ExecutionError] = None,
        execution_count: Optional[int] = None,
        **kwargs,
    ):
        self.results = results or []
        self.logs = logs or Logs()
        self.error = error
        self.execution_count = execution_count

    def __repr__(self):
        return f"Execution(results={self.results}, logs={self.logs}, error={self.error}, execution_count={self.execution_count})"

    @property
    def text(self) -> Optional[str]:
        """
        Returns the text representation of the main result.

        :return: The text representation of the main result.
        """
        for result in self.results:
            if result.is_main_result:
                return result.text
        return None

    def to_json(self) -> str:
        """
        Returns the JSON representation of the Execution object.
        """
        data = {
            "results": [self._serialize_result(result) for result in self.results],
            "logs": self.logs.to_json(),
            "error": self.error.to_json() if self.error else None,
            "execution_count": self.execution_count,
        }
        return json.dumps(data)

    def _serialize_result(self, result: Result) -> Dict[str, Any]:
        """Serialize a single result to JSON-serializable format."""
        serialized = {
            "exit_code": result.exit_code,
            "started_at": result.started_at.isoformat() if result.started_at else None,
            "finished_at": (
                result.finished_at.isoformat() if result.finished_at else None
            ),
            "text": result.text,
            "html": result.html,
            "markdown": result.markdown,
            "svg": result.svg,
            "png": result.png,
            "jpeg": result.jpeg,
            "pdf": result.pdf,
            "latex": result.latex,
            "json": result.json_data,
            "javascript": result.javascript,
            "data": result.data,
            "execution_count": result.execution_count,
            "is_main_result": result.is_main_result,
            "extra": result.extra,
        }

        # Remove None values
        return {k: v for k, v in serialized.items() if v is not None}


@dataclass
class Context:
    """
    Represents a context for code execution.
    """

    id: str
    """The ID of the context."""
    language: str
    """The language of the context."""
    cwd: str
    """The working directory of the context."""

    def __init__(self, context_id: str, language: str, cwd: str, **kwargs):
        self.id = context_id
        self.language = language
        self.cwd = cwd

    @classmethod
    def from_json(cls, data: Dict[str, str]):
        return cls(
            context_id=data.get("id"),
            language=data.get("language"),
            cwd=data.get("cwd"),
        )


def parse_output(
    execution: Execution,
    output: api_pb2.ExecuteResponse,
    on_stdout: Optional[OutputHandler[OutputMessage]] = None,
    on_stderr: Optional[OutputHandler[OutputMessage]] = None,
    on_result: Optional[OutputHandler[Result]] = None,
    on_error: Optional[OutputHandler[ExecutionError]] = None,
):
    """
    Parse the output from the execution service and update the execution object.
    """
    if output.HasField("stdout"):
        content = output.stdout.content
        execution.logs.stdout.append(content)
        if on_stdout:
            message = OutputMessage(
                content=content,
                timestamp=int(datetime.now().timestamp() * 1e9),
                error=False,
            )
            if asyncio.iscoroutinefunction(on_stdout):
                asyncio.create_task(on_stdout(message))
            else:
                on_stdout(message)

    elif output.HasField("stderr"):
        content = output.stderr.content
        execution.logs.stderr.append(content)
        if on_stderr:
            message = OutputMessage(
                content=content,
                timestamp=int(datetime.now().timestamp() * 1e9),
                error=True,
            )
            if asyncio.iscoroutinefunction(on_stderr):
                asyncio.create_task(on_stderr(message))
            else:
                on_stderr(message)

    elif output.HasField("result"):
        result_msg = output.result
        result = Result(
            exit_code=result_msg.exit_code,
            started_at=result_msg.started_at,
            finished_at=result_msg.finished_at,
            text=result_msg.text,
            html=result_msg.html,
            markdown=result_msg.markdown,
            svg=result_msg.svg,
            png=result_msg.png,
            jpeg=result_msg.jpeg,
            pdf=result_msg.pdf,
            latex=result_msg.latex,
            json=result_msg.json,
            javascript=result_msg.javascript,
            data=result_msg.data,
            chart=result_msg.chart,
            execution_count=result_msg.execution_count,
            is_main_result=result_msg.is_main_result,
            extra=dict(result_msg.extra),
        )
        execution.results.append(result)
        if on_result:
            if asyncio.iscoroutinefunction(on_result):
                asyncio.create_task(on_result(result))
            else:
                on_result(result)

        # Update execution count if this is the main result
        if result.is_main_result and result.execution_count is not None:
            execution.execution_count = result.execution_count

    elif output.HasField("error"):
        error_msg = output.error
        error = ExecutionError(
            name=error_msg.name,
            value=error_msg.value,
            traceback=error_msg.traceback,
        )
        execution.error = error
        if on_error:
            if asyncio.iscoroutinefunction(on_error):
                asyncio.create_task(on_error(error))
            else:
                on_error(error)


async def aextract_exception(res: Response):
    """Asynchronously extract exception from response."""
    if res.is_success:
        return None

    await res.aread()
    return extract_exception(res)


def extract_exception(res: Response):
    """Extract exception from response."""
    if res.is_success:
        return None

    res.read()
    return format_exception(res)


def format_exception(res: Response):
    """Format exception from response."""
    if res.is_success:
        return None

    if res.status_code == 404:
        return NotFoundException(res.text)
    elif res.status_code == 502:
        return TimeoutException(
            f"{res.text}: This error is likely due to sandbox timeout. You can modify the sandbox timeout by passing 'timeout' when starting the sandbox or calling '.set_timeout' on the sandbox with the desired timeout."
        )
    else:
        return SandboxException(f"{res.status_code}: {res.text}")
