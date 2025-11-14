from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from httpx import Limits

from ..api.client.models import SandboxState


@dataclass
class SandboxInfo:
    """Information about a sandbox."""

    sandbox_id: str
    """Sandbox ID."""
    sandbox_domain: Optional[str]
    """Domain where the sandbox is hosted."""
    template_id: str
    """Template ID."""
    name: Optional[str]
    """Template name."""
    metadata: Dict[str, str]
    """Saved sandbox metadata."""
    started_at: datetime
    """Sandbox start time."""
    uptime: int
    """Sandbox up time."""
    end_at: datetime
    """Sandbox expiration date."""
    timeout: int
    """Sandbox timeout."""
    envd_version: Optional[str]
    """Envd version."""
    _envd_access_token: Optional[str]
    """Envd access token."""
    object_storage: Optional[Dict[str, str]]
    """Object storage."""


@dataclass
class ListedSandbox:
    """Information about a sandbox."""

    sandbox_id: str
    """Sandbox ID."""
    template_id: str
    """Template ID."""
    name: Optional[str]
    """Template Alias."""
    state: SandboxState
    """Sandbox state."""
    cpu_count: int
    """Sandbox CPU count."""
    memory_mb: int
    """Sandbox Memory size in MB."""
    metadata: Dict[str, str]
    """Saved sandbox metadata."""
    started_at: datetime
    """Sandbox start time."""
    uptime: int
    """Sandbox up time."""
    end_at: datetime
    """Sandbox expiration date."""
    timeout: int
    """Sandbox timeout."""
    object_storage: Optional[Dict[str, str]]
    """Object storage."""


@dataclass
class SandboxQuery:
    """Query parameters for listing sandboxes."""

    metadata: Optional[dict[str, str]] = None
    """Filter sandboxes by metadata."""


@dataclass
class SandboxMetrics:
    """Sandbox metrics."""

    cpu_count: int
    """Number of CPUs."""
    cpu_used_pct: float
    """CPU usage percentage."""
    disk_total: int
    """Total disk space in bytes."""
    disk_used: int
    """Disk used in bytes."""
    mem_total: int
    """Total memory in bytes."""
    mem_used: int
    """Memory used in bytes."""
    timestamp: datetime
    """Timestamp of the metric entry."""


class SandboxApiBase(ABC):
    _limits = Limits(
        max_keepalive_connections=10,
        max_connections=20,
        keepalive_expiry=20,
    )
    default_sandbox_timeout = 300
