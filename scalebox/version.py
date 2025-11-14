"""
Version information for ScaleBox Python SDK
"""

__version__ = "0.1.17"
__version_info__ = (0, 1, 17)


def get_version() -> str:
    """Get the current version string."""
    return __version__


def get_version_info() -> tuple[int, int, int]:
    """Get the current version info tuple."""
    return __version_info__
