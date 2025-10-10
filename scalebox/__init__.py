"""
ScaleBox Python SDK

A multi-language code execution sandbox with support for:
- Python, R, Node.js, Deno/TypeScript, Java, and Bash
- Synchronous and asynchronous execution
- Persistent context across executions
- Rich result formats (text, HTML, Markdown, SVG, images, LaTeX, JSON, etc.)
- Real-time callbacks and monitoring
"""

__version__ = "0.1.0"
__author__ = "ScaleBox Team"
__email__ = "dev@scalebox.dev"

# Core imports
from .code_interpreter import Sandbox, AsyncSandbox
from .code_interpreter.models import (
    Context,
    Execution,
    ExecutionError,
    Result,
    MIMEType,
    Logs,
    OutputHandler,
    OutputMessage,
)
from .exceptions import (
    SandboxException,
    TimeoutException,
    InvalidArgumentException,
    NotEnoughSpaceException,
    NotFoundException,
    AuthenticationException,
    TemplateException,
    RateLimitException,
)
from .connection_config import ConnectionConfig

# API client imports
from .api.client import Client
from .api.client.errors import APIError

# Sandbox imports
from .sandbox import Sandbox as BaseSandbox
from .sandbox_async import AsyncSandbox as BaseAsyncSandbox

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
