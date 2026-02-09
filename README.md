# Scalebox Python SDK

[![CI/CD Pipeline](https://github.com/scalebox-dev/scalebox-sdk-python/actions/workflows/ci.yml/badge.svg)](https://github.com/scalebox-dev/scalebox-sdk-python/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/scalebox-sdk.svg)](https://pypi.org/project/scalebox-sdk/)
[![Downloads](https://img.shields.io/pypi/dm/scalebox-sdk.svg)](https://pypi.org/project/scalebox-sdk/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Check: MyPy](https://img.shields.io/badge/type%20check-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Linting: Flake8](https://img.shields.io/badge/linting-flake8-green.svg)](https://flake8.pycqa.org/)
[![Import Sorting: isort](https://img.shields.io/badge/imports-isort-blue.svg)](https://pycqa.github.io/isort/)
[![Multi-Language Support](https://img.shields.io/badge/languages-Python%20%7C%20R%20%7C%20Node.js%20%7C%20TypeScript%20%7C%20Java%20%7C%20Bash-orange.svg)](https://github.com/scalebox-dev/scalebox-sdk-python)

> [中文文档](./README_CN.md)

A Python SDK for executing multi-language code in a controlled sandbox environment, supporting both synchronous and asynchronous modes, along with multi-language kernels (Python, R, Node.js, Deno/TypeScript, Java/IJAVA, Bash). Comprehensive real-world test cases and scripts are provided.

## Features
- **Multi-language kernels**: Python, R, Node.js, Deno/TypeScript, Java/IJAVA, Bash
- **Execution modes**: Synchronous `Sandbox` and asynchronous `AsyncSandbox`
- **Persistent context**: Retain variables/state across multiple executions
- **Callback subscriptions**: stdout, stderr, results, and errors
- **Rich result formats**: text, html, markdown, svg, png, jpeg, pdf, latex, json, javascript, chart, data, and more
- **Real-world testing**: Comprehensive test coverage for sync/async and multi-language examples

## Requirements
- Python 3.12+
- Accessible Scalebox environment or local service

## Installation

```bash

# Recommended: use a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r scalebox-sdk
```

## Configuration
Credentials can be read from environment variables or a `.env` file:

- `SBX_API_KEY`

Example:
```env
# .env
SBX_API_KEY=***
```
Or:
```bash
export SBX_API_KEY=***
```

Optional: Use `python-dotenv` to automatically load `.env`:
```bash
pip install python-dotenv
```

## Quick Start (Synchronous)
```python
from dotenv import load_dotenv; load_dotenv()
from scalebox.code_interpreter import Sandbox

sandbox = Sandbox.create()  # Default lifetime: 5 minutes
execution = sandbox.run_code("print('hello world')", language="python")
print(execution.logs.stdout)

files = sandbox.files.list("/")
print(files)
```

## Quick Start (Asynchronous)
```python
import asyncio
from dotenv import load_dotenv; load_dotenv()
from scalebox.code_interpreter import AsyncSandbox

async def main():
    sandbox = await AsyncSandbox.create()
    exec_ = await sandbox.run_code("print('async hello')", language="python")
    print(exec_.logs.stdout)

asyncio.run(main())
```

## Multi-Language Examples
- Python: `language="python"`
- R: `language="r"`
- Node.js: `language="nodejs"`
- Deno/TypeScript: `language="typescript"`
- Java (IJAVA/pure Java): `language="ijava"` or `language="java"`
- Bash: `language="bash"`

### Node.js Example:
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
code = """
console.log("Hello from Node.js!");
const x = 1 + 2; console.log(`x=${x}`);
"""
result = sbx.run_code(code, language="nodejs")
print(result.logs.stdout)
```

### R Example:
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
code = """
print("Hello from R!")
x <- mean(c(1,2,3,4,5))
print(paste("mean:", x))
"""
res = sbx.run_code(code, language="r")
print(res.logs.stdout)
```

### Deno/TypeScript Example:
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
ts = """
console.log("Hello from Deno/TypeScript!")
const nums: number[] = [1,2,3]
console.log(nums.reduce((a,b)=>a+b, 0))
"""
res = sbx.run_code(ts, language="typescript")
print(res.logs.stdout)
```

### Java/IJAVA Example:
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
code = """
System.out.println("Hello from IJAVA!");
int a = 10, b = 20; System.out.println(a + b);
"""
res = sbx.run_code(code, language="java")
print(res.logs.stdout)
```

### Bash Example:
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
res = sbx.run_code("echo 'Hello from Bash'", language="bash")
print(res.logs.stdout)
```

## Context Management
Context allows you to reuse variables/state across multiple executions:
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
ctx = sbx.create_code_context(language="python", cwd="/tmp")

sbx.run_code("counter = 0", context=ctx)
sbx.run_code("counter += 1; print(counter)", context=ctx)
# Must clean up when done
sbx.destroy_context(ctx)
```

Async API:
```python
from scalebox.code_interpreter import AsyncSandbox

async def demo():
    sbx = await AsyncSandbox.create()
    ctx = await sbx.create_code_context(language="python", cwd="/tmp")
    await sbx.run_code("counter = 0", context=ctx)
    await sbx.run_code("counter += 1; print(counter)", context=ctx)
    await sbx.destroy_context(ctx)
```

## Callbacks (Optional)
```python
from scalebox.code_interpreter import Sandbox
from scalebox.code_interpreter import OutputMessage, Result, ExecutionError

sbx = Sandbox.create()

def on_stdout(msg: OutputMessage):
    print("STDOUT:", msg.content)

def on_stderr(msg: OutputMessage):
    print("STDERR:", msg.content)

def on_result(res: Result):
    print("RESULT formats:", list(res.formats()))

def on_error(err: ExecutionError):
    print("ERROR:", err.name, err.value)

sbx.run_code(
    "print('with callbacks')",
    language="python",
    on_stdout=on_stdout,
    on_stderr=on_stderr,
    on_result=on_result,
    on_error=on_error,
)
```

## Result Formats
`Result` may contain the following data fields:
- `text`, `html`, `markdown`, `svg`, `png`, `jpeg`, `pdf`, `latex`
- `json_data`, `javascript`, `data`, `chart`
- `execution_count`, `is_main_result`, `extra`

Use `list(result.formats())` to view available formats.

## Running Tests
The `test/` directory contains comprehensive real-world use cases (not unittest-style, direct script-style), covering:
- Synchronous and asynchronous comprehensive test cases
- Multi-language kernels (Python, R, Node.js, Deno/TypeScript, Java/IJAVA, Bash)
- Context management, callbacks, and result formats

Run syntax checks:
```bash
cd test
python3 -m py_compile test_code_interpreter_sync_comprehensive.py
python3 -m py_compile test_code_interpreter_async_comprehensive.py
```

It's recommended to prepare dependencies in a virtual environment and install language runtimes (such as R, Node, Deno, JDK/IJAVA, etc.) as needed, ensuring each kernel can be executed by the backend.

## Version Management

This project uses automated version management with support for Semantic Versioning.

### 🚀 Automatic Version Bumping

Use the built-in script to bump versions:

```bash
# Bump patch version (0.1.1 -> 0.1.2)
python scripts/bump_version.py patch

# Bump minor version (0.1.1 -> 0.2.0)
python scripts/bump_version.py minor

# Bump major version (0.1.1 -> 1.0.0)
python scripts/bump_version.py major
```

### 📦 Automated Release Process

#### 🚀 Method 1: GitHub Actions One-Click Bump (Recommended)

1. **Navigate to GitHub Actions page**
2. **Select "CI/CD Pipeline" workflow**
3. **Click "Run workflow" button**
4. **Select version type**:
   - `patch`: Patch version (0.1.1 → 0.1.2)
   - `minor`: Minor version (0.1.1 → 0.2.0)  
   - `major`: Major version (0.1.1 → 1.0.0)
5. **Select auto-commit option**
6. **Click run** - The system will automatically complete all steps!

#### 🔧 Method 2: Local Script Bump

1. **Version Bump**: Use `bump_version.py` script
2. **GitHub Actions**: Automatically build and publish to PyPI
3. **Trigger Conditions**:
   - Push to `main` branch
   - Create `v*` tag (e.g., `v0.1.2`)

### 🔧 Version File Synchronization

The script automatically updates versions in the following files:
- `scalebox/__init__.py`
- `scalebox/version.py`
- `pyproject.toml`
- `CHANGELOG.md` (optional)

### 📋 Release Steps

```bash
# 1. Bump version
python scripts/bump_version.py patch

# 2. Check changes
git diff

# 3. Commit changes
git add .
git commit -m "Bump version to 0.1.2"

# 4. Push and create tag
git push origin main
git push origin --tags

# 5. GitHub Actions will automatically publish to PyPI
```

### 🏷️ Version Rules

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible feature additions
- **PATCH**: Backward-compatible bug fixes

## Troubleshooting
- **Import/dependency errors**: Ensure venv is activated and all required dependencies from `scalebox/requirements.txt` are installed
- **`ModuleNotFoundError`**: Add the project root path to `sys.path` in test scripts, or run from the project root directory
- **External kernels unavailable**: Ensure the environment has the corresponding language runtime installed (R/Node/Deno/JDK) and the backend has enabled that kernel
- **Timeout/network issues**: Check network connectivity and backend service accessibility, increase `timeout`/`request_timeout` if necessary

## License
This project is licensed under the terms of the LICENSE file in the repository.
