"""
ScaleBox Python SDK

A multi-language code execution sandbox with support for:
- Python, R, Node.js, Deno/TypeScript, Java, and Bash
- Synchronous and asynchronous execution
- Persistent context across executions
- Rich result formats (text, HTML, Markdown, SVG, images, LaTeX, JSON, etc.)
- Real-time callbacks and monitoring
"""

__version__ = "0.1.4"
__author__ = "ScaleBox Team"
__email__ = "dev@scalebox.dev"

# API client imports
from .api.client import Client
from .api.client.errors import UnexpectedStatus

# Core imports
from .code_interpreter import AsyncSandbox, Sandbox
from .code_interpreter.models import (
    Context,
    Execution,
    ExecutionError,
    Logs,
    MIMEType,
    OutputHandler,
    OutputMessage,
    Result,
)
from .connection_config import ConnectionConfig
from .exceptions import (
    AuthenticationException,
    InvalidArgumentException,
    NotEnoughSpaceException,
    NotFoundException,
    RateLimitException,
    SandboxException,
    TemplateException,
    TimeoutException,
)
from .sandbox_async.main import AsyncSandbox as BaseAsyncSandbox

# Sandbox imports
from .sandbox_sync.main import Sandbox as BaseSandbox

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Core classes
    "Sandbox",
    "AsyncSandbox",
    "BaseSandbox",
    "BaseAsyncSandbox",
    "Client",
    # Models
    "Context",
    "Execution",
    "ExecutionError",
    "Result",
    "MIMEType",
    "Logs",
    "OutputHandler",
    "OutputMessage",
    # Exceptions
    "SandboxException",
    "TimeoutException",
    "InvalidArgumentException",
    "NotEnoughSpaceException",
    "NotFoundException",
    "AuthenticationException",
    "TemplateException",
    "RateLimitException",
    "APIError",
    # Configuration
    "ConnectionConfig",
]
