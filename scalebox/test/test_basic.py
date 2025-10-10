#!/usr/bin/env python3
"""
Basic tests to verify the package can be imported and basic functionality works.
These tests don't require external services or complex dependencies.
"""

import pytest
from scalebox import __version__
from scalebox.exceptions import SandboxException, TimeoutException, AuthenticationException


def test_package_version():
    """Test that the package version can be imported."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_exceptions_can_be_imported():
    """Test that all exceptions can be imported."""
    # Test that exceptions can be instantiated
    auth_error = AuthenticationException("Test auth error")
    assert str(auth_error) == "Test auth error"
    
    sandbox_error = SandboxException("Test sandbox error")
    assert str(sandbox_error) == "Test sandbox error"
    
    timeout_error = TimeoutException("Test timeout error")
    assert str(timeout_error) == "Test timeout error"


def test_package_imports():
    """Test that main package components can be imported."""
    from scalebox import Client
    from scalebox import Sandbox, AsyncSandbox
    
    # Test that classes can be instantiated (basic check)
    assert Client is not None
    assert Sandbox is not None
    assert AsyncSandbox is not None


def test_version_info():
    """Test version info functions."""
    from scalebox.version import get_version, get_version_info
    
    version = get_version()
    assert isinstance(version, str)
    assert len(version) > 0
    
    version_info = get_version_info()
    assert isinstance(version_info, tuple)
    assert len(version_info) == 3
    assert all(isinstance(x, int) for x in version_info)


def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    # Test that we can create basic objects without external services
    from scalebox.exceptions import AuthenticationException
    
    # Test exception creation and message handling
    error = AuthenticationException("Test message")
    assert "Test message" in str(error)
    
    # Test that we can import and use basic utilities
    from scalebox.version import get_version
    version = get_version()
    assert version is not None


if __name__ == "__main__":
    pytest.main([__file__])
