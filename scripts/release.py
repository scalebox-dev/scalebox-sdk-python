#!/usr/bin/env python3
"""
Release script for ScaleBox Python SDK
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> str:
    """Run a shell command and return its output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def get_current_version() -> str:
    """Get the current version from pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        content = f.read()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def update_version(new_version: str):
    """Update version in pyproject.toml and __init__.py."""
    # Update pyproject.toml
    with open("pyproject.toml", "r") as f:
        content = f.read()
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    with open("pyproject.toml", "w") as f:
        f.write(content)
    
    # Update __init__.py
    with open("scalebox/__init__.py", "r") as f:
        content = f.read()
    content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
    with open("scalebox/__init__.py", "w") as f:
        f.write(content)
    
    # Update version.py
    with open("scalebox/version.py", "r") as f:
        content = f.read()
    content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
    with open("scalebox/version.py", "w") as f:
        f.write(content)


def main():
    """Main release function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/release.py <version>")
        print("Example: python scripts/release.py 0.1.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    current_version = get_current_version()
    
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    # Check if we're on main branch
    branch = run_command("git branch --show-current")
    if branch != "main":
        print("Warning: Not on main branch")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check for uncommitted changes
    status = run_command("git status --porcelain")
    if status:
        print("Error: You have uncommitted changes")
        print(status)
        sys.exit(1)
    
    # Update version
    print("Updating version...")
    update_version(new_version)
    
    # Run tests
    print("Running tests...")
    run_command("python -m pytest scalebox/test -v")
    
    # Build package
    print("Building package...")
    run_command("python -m build")
    
    # Check package
    print("Checking package...")
    run_command("twine check dist/*")
    
    # Commit changes
    print("Committing changes...")
    run_command(f"git add pyproject.toml scalebox/__init__.py scalebox/version.py")
    run_command(f'git commit -m "Release version {new_version}"')
    run_command(f"git tag v{new_version}")
    
    print(f"Release {new_version} is ready!")
    print("To publish to PyPI, run:")
    print("  twine upload dist/*")
    print("To push to GitHub, run:")
    print(f"  git push origin main --tags")


if __name__ == "__main__":
    main()
