"""
Version information for ScaleBox Python SDK
"""

__version__ = "1.0.3"
__version_info__ = (1, 0, 3)


def get_version() -> str:
    """Get the current version string."""
    return __version__


def get_version_info() -> tuple[int, int, int]:
    """Get the current version info tuple."""
    return __version_info__
