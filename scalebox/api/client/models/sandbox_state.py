from enum import Enum


class SandboxState(str, Enum):
    PAUSED = "paused"
    RUNNING = "running"
    TERMINATED = "terminated"

    def __str__(self) -> str:
        return str(self.value)
