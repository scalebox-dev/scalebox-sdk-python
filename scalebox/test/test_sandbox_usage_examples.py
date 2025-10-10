#!/usr/bin/env python3
"""
Comprehensive usage examples and best practices for both sandbox modules.

This file demonstrates:
- Real-world usage scenarios
- Best practices for different use cases
- Code patterns and idioms
- Integration examples
- Performance optimization techniques
- Error handling strategies
"""

import asyncio
import datetime
import json
import logging
import os
import tempfile
import threading
import time
from contextlib import contextmanager, asynccontextmanager
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from scalebox.sandbox_async.main import AsyncSandbox
from scalebox.sandbox_sync.main import Sandbox
from scalebox.sandbox.commands.command_handle import PtySize
from scalebox.sandbox.filesystem.filesystem import EntryInfo, WriteInfo
from scalebox.exceptions import SandboxException

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ======================== 工具类和辅助函数 ========================


class SandboxManager:
    """沙箱管理器 - 展示资源管理最佳实践"""

    def __init__(self, template: str = "base", max_concurrent: int = 5):
        self.template = template
        self.max_concurrent = max_concurrent
        self._active_sandboxes: Dict[str, Sandbox] = {}
        self._lock = (
            asyncio.Lock() if asyncio.iscoroutinefunction(self.__class__) else None
        )

    @contextmanager
    def get_sandbox(self, sandbox_id: Optional[str] = None):
        """上下文管理器获取沙箱"""
        sandbox = None
        created_new = False

        try:
            if sandbox_id and sandbox_id in self._active_sandboxes:
                sandbox = self._active_sandboxes[sandbox_id]
            else:
                sandbox = Sandbox(template=self.template)
                sandbox_id = sandbox.sandbox_id
                self._active_sandboxes[sandbox_id] = sandbox
                created_new = True
                logger.info(f"创建新沙箱: {sandbox_id}")

            yield sandbox

        except Exception as e:
            logger.error(f"沙箱操作异常: {e}")
            raise
        finally:
            if created_new and sandbox:
                try:
                    sandbox.kill()
                    self._active_sandboxes.pop(sandbox_id, None)
                    logger.info(f"清理沙箱: {sandbox_id}")
                except Exception as e:
                    logger.error(f"清理沙箱失败: {e}")


class AsyncSandboxManager:
    """异步沙箱管理器"""

    def __init__(self, template: str = "base", max_concurrent: int = 10):
        self.template = template
        self.max_concurrent = max_concurrent
        self._active_sandboxes: Dict[str, AsyncSandbox] = {}
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrent)

    @asynccontextmanager
    async def get_sandbox(self, sandbox_id: Optional[str] = None):
        """异步上下文管理器获取沙箱"""
        async with self._semaphore:  # 限制并发数
            sandbox = None
            created_new = False

            try:
                async with self._lock:
                    if sandbox_id and sandbox_id in self._active_sandboxes:
                        sandbox = self._active_sandboxes[sandbox_id]
                    else:
                        sandbox = await AsyncSandbox.create(template=self.template)
                        sandbox_id = sandbox.sandbox_id
                        self._active_sandboxes[sandbox_id] = sandbox
                        created_new = True
                        logger.info(f"创建新异步沙箱: {sandbox_id}")

                yield sandbox

            except Exception as e:
                logger.error(f"异步沙箱操作异常: {e}")
                raise
            finally:
                if created_new and sandbox:
                    try:
                        await sandbox.kill()
                        async with self._lock:
                            self._active_sandboxes.pop(sandbox_id, None)
                        logger.info(f"清理异步沙箱: {sandbox_id}")
                    except Exception as e:
                        logger.error(f"清理异步沙箱失败: {e}")


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"尝试 {attempt + 1}/{max_retries} 失败: {e}, {delay}秒后重试"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"所有重试失败: {e}")
            raise last_exception

        return wrapper

    return decorator


def async_retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """异步重试装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"异步尝试 {attempt + 1}/{max_retries} 失败: {e}, {delay}秒后重试"
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"所有异步重试失败: {e}")
            raise last_exception

        return wrapper

    return decorator


# ======================== 实际使用场景示例 ========================


class CodeExecutionService:
    """代码执行服务 - 展示实际应用场景"""

    def __init__(self, use_async: bool = False):
        self.use_async = use_async
        if use_async:
            self.sandbox_manager = AsyncSandboxManager()
        else:
            self.sandbox_manager = SandboxManager()

    def execute_python_code(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """执行Python代码"""
        with self.sandbox_manager.get_sandbox() as sandbox:
            # 创建Python文件
            code_file = "/tmp/user_code.py"
            sandbox.files.write(code_file, code)

            # 执行代码
            result = sandbox.commands.run(
                f"cd /tmp && timeout {timeout} python3 user_code.py",
                timeout=timeout + 5,
            )

            return {
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": time.time(),
                "timed_out": result.exit_code == 124,  # timeout命令的退出码
            }

    async def async_execute_python_code(
        self, code: str, timeout: int = 30
    ) -> Dict[str, Any]:
        """异步执行Python代码"""
        async with self.sandbox_manager.get_sandbox() as sandbox:
            # 创建Python文件
            code_file = "/tmp/async_user_code.py"
            await sandbox.files.write(code_file, code)

            # 异步执行代码
            result = await sandbox.commands.run(
                f"cd /tmp && timeout {timeout} python3 async_user_code.py",
                timeout=timeout + 5,
            )

            return {
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": time.time(),
                "timed_out": result.exit_code == 124,
            }


class FileProcessingService:
    """文件处理服务 - 展示文件操作最佳实践"""

    @retry_on_failure(max_retries=3)
    def process_files_batch(
        self, files_data: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """批量处理文件"""
        with SandboxManager().get_sandbox() as sandbox:
            results = []

            # 批量写入文件
            write_operations = [
                {"path": f"/tmp/{file_info['name']}", "data": file_info["content"]}
                for file_info in files_data
            ]

            written_files = sandbox.files.write(write_operations)
            logger.info(f"成功写入 {len(written_files)} 个文件")

            # 处理每个文件
            for file_info in files_data:
                file_path = f"/tmp/{file_info['name']}"

                # 获取文件信息
                file_stats = sandbox.files.get_info(file_path)

                # 根据文件类型进行处理
                if file_info["name"].endswith(".txt"):
                    # 文本文件：统计行数和字符数
                    result = sandbox.commands.run(f"wc -l -c {file_path}")
                    lines_chars = result.stdout.strip().split()

                    results.append(
                        {
                            "name": file_info["name"],
                            "size": file_stats.size,
                            "lines": int(lines_chars[0]) if len(lines_chars) > 0 else 0,
                            "chars": int(lines_chars[1]) if len(lines_chars) > 1 else 0,
                            "type": "text",
                        }
                    )

                elif file_info["name"].endswith(".json"):
                    # JSON文件：验证格式
                    content = sandbox.files.read(file_path)
                    try:
                        json.loads(content)
                        valid_json = True
                        error = None
                    except json.JSONDecodeError as e:
                        valid_json = False
                        error = str(e)

                    results.append(
                        {
                            "name": file_info["name"],
                            "size": file_stats.size,
                            "valid_json": valid_json,
                            "error": error,
                            "type": "json",
                        }
                    )

                else:
                    # 其他文件：基本信息
                    results.append(
                        {
                            "name": file_info["name"],
                            "size": file_stats.size,
                            "type": "other",
                        }
                    )

                # 清理文件
                sandbox.files.remove(file_path)

            return results

    @async_retry_on_failure(max_retries=3)
    async def async_process_files_batch(
        self, files_data: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """异步批量处理文件"""
        async with AsyncSandboxManager().get_sandbox() as sandbox:
            # 批量异步写入文件
            write_operations = [
                {"path": f"/tmp/{file_info['name']}", "data": file_info["content"]}
                for file_info in files_data
            ]

            written_files = await sandbox.files.write(write_operations)
            logger.info(f"异步成功写入 {len(written_files)} 个文件")

            # 并发处理文件
            async def process_single_file(file_info: Dict[str, str]) -> Dict[str, Any]:
                file_path = f"/tmp/{file_info['name']}"

                # 获取文件信息
                file_stats = await sandbox.files.get_info(file_path)

                # 根据文件类型进行异步处理
                if file_info["name"].endswith(".txt"):
                    result = await sandbox.commands.run(f"wc -l -c {file_path}")
                    lines_chars = result.stdout.strip().split()

                    await sandbox.files.remove(file_path)  # 异步清理

                    return {
                        "name": file_info["name"],
                        "size": file_stats.size,
                        "lines": int(lines_chars[0]) if len(lines_chars) > 0 else 0,
                        "chars": int(lines_chars[1]) if len(lines_chars) > 1 else 0,
                        "type": "text",
                    }

                elif file_info["name"].endswith(".json"):
                    content = await sandbox.files.read(file_path)
                    try:
                        json.loads(content)
                        valid_json = True
                        error = None
                    except json.JSONDecodeError as e:
                        valid_json = False
                        error = str(e)

                    await sandbox.files.remove(file_path)

                    return {
                        "name": file_info["name"],
                        "size": file_stats.size,
                        "valid_json": valid_json,
                        "error": error,
                        "type": "json",
                    }

                else:
                    await sandbox.files.remove(file_path)
                    return {
                        "name": file_info["name"],
                        "size": file_stats.size,
                        "type": "other",
                    }

            # 并发执行所有文件处理任务
            tasks = [process_single_file(file_info) for file_info in files_data]
            results = await asyncio.gather(*tasks)

            return results


class InteractiveSession:
    """交互式会话 - 展示PTY使用最佳实践"""

    def __init__(self, sandbox: Union[Sandbox, AsyncSandbox]):
        self.sandbox = sandbox
        self.is_async = isinstance(sandbox, AsyncSandbox)
        self.session_log = []

    def start_interactive_python(self):
        """启动交互式Python会话"""
        if self.is_async:
            raise ValueError("请使用 async_start_interactive_python 对于异步沙箱")

        def output_handler(data):
            self.session_log.append(("output", data, time.time()))
            print(f"Python> {data.strip()}")

        # 创建PTY
        self.pty = self.sandbox.pty.create(
            size=PtySize(rows=24, cols=80),
            on_data=output_handler,
            envs={"PYTHONPATH": "/tmp", "PYTHONUNBUFFERED": "1"},
        )

        # 启动Python解释器
        self.sandbox.pty.send_stdin(self.pty.pid, b"python3 -i\n")
        time.sleep(2)  # 等待Python启动

        return self.pty

    async def async_start_interactive_python(self):
        """启动异步交互式Python会话"""
        if not self.is_async:
            raise ValueError("请使用 start_interactive_python 对于同步沙箱")

        async def output_handler(data):
            self.session_log.append(("output", data, time.time()))
            print(f"AsyncPython> {data.strip()}")

        # 创建PTY
        self.pty = await self.sandbox.pty.create(
            size=PtySize(rows=24, cols=80),
            on_data=output_handler,
            envs={"PYTHONPATH": "/tmp", "PYTHONUNBUFFERED": "1"},
        )

        # 启动Python解释器
        await self.sandbox.pty.send_stdin(self.pty.pid, b"python3 -i\n")
        await asyncio.sleep(2)  # 等待Python启动

        return self.pty

    def execute_command(self, command: str):
        """在交互式会话中执行命令"""
        if self.is_async:
            raise ValueError("请使用 async_execute_command 对于异步沙箱")

        self.session_log.append(("input", command, time.time()))
        self.sandbox.pty.send_stdin(self.pty.pid, f"{command}\n".encode())
        time.sleep(1)  # 等待命令执行

    async def async_execute_command(self, command: str):
        """在异步交互式会话中执行命令"""
        if not self.is_async:
            raise ValueError("请使用 execute_command 对于同步沙箱")

        self.session_log.append(("input", command, time.time()))
        await self.sandbox.pty.send_stdin(self.pty.pid, f"{command}\n".encode())
        await asyncio.sleep(1)  # 等待命令执行

    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        inputs = [entry for entry in self.session_log if entry[0] == "input"]
        outputs = [entry for entry in self.session_log if entry[0] == "output"]

        return {
            "total_commands": len(inputs),
            "total_outputs": len(outputs),
            "session_duration": (
                self.session_log[-1][2] - self.session_log[0][2]
                if self.session_log
                else 0
            ),
            "commands": [entry[1] for entry in inputs],
        }


# ======================== 性能优化示例 ========================


class OptimizedFileOperations:
    """优化的文件操作 - 展示性能优化技巧"""

    @staticmethod
    def batch_file_operations_sync(sandbox: Sandbox, operations: List[Dict[str, Any]]):
        """同步批量文件操作优化"""
        # 按操作类型分组
        writes = [op for op in operations if op["type"] == "write"]
        reads = [op for op in operations if op["type"] == "read"]

        results = {}

        # 批量写入
        if writes:
            write_data = [{"path": op["path"], "data": op["data"]} for op in writes]
            write_results = sandbox.files.write(write_data)
            results["writes"] = write_results

        # 批量读取（如果支持）
        if reads:
            read_results = []
            for op in reads:
                content = sandbox.files.read(op["path"])
                read_results.append({"path": op["path"], "content": content})
            results["reads"] = read_results

        return results

    @staticmethod
    async def batch_file_operations_async(
        sandbox: AsyncSandbox, operations: List[Dict[str, Any]]
    ):
        """异步批量文件操作优化"""
        # 按操作类型分组
        writes = [op for op in operations if op["type"] == "write"]
        reads = [op for op in operations if op["type"] == "read"]

        results = {}

        # 批量写入
        if writes:
            write_data = [{"path": op["path"], "data": op["data"]} for op in writes]
            write_results = await sandbox.files.write(write_data)
            results["writes"] = write_results

        # 并发读取
        if reads:

            async def read_file(path):
                content = await sandbox.files.read(path)
                return {"path": path, "content": content}

            read_tasks = [read_file(op["path"]) for op in reads]
            read_results = await asyncio.gather(*read_tasks)
            results["reads"] = read_results

        return results


class CommandExecutionPool:
    """命令执行池 - 展示命令执行优化"""

    def __init__(self, sandbox: Sandbox, max_concurrent: int = 5):
        self.sandbox = sandbox
        self.max_concurrent = max_concurrent
        self._semaphore = threading.Semaphore(max_concurrent)
        self._lock = threading.Lock()
        self.results = []

    def execute_commands_concurrent(self, commands: List[str]) -> List[Dict[str, Any]]:
        """并发执行命令（使用线程池）"""
        import concurrent.futures

        def execute_single_command(cmd):
            with self._semaphore:
                try:
                    result = self.sandbox.commands.run(cmd)
                    return {
                        "command": cmd,
                        "exit_code": result.exit_code,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "success": result.exit_code == 0,
                    }
                except Exception as e:
                    return {"command": cmd, "error": str(e), "success": False}

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent
        ) as executor:
            futures = [executor.submit(execute_single_command, cmd) for cmd in commands]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        return results


class AsyncCommandExecutionPool:
    """异步命令执行池"""

    def __init__(self, sandbox: AsyncSandbox, max_concurrent: int = 10):
        self.sandbox = sandbox
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_commands_concurrent(
        self, commands: List[str]
    ) -> List[Dict[str, Any]]:
        """异步并发执行命令"""

        async def execute_single_command(cmd):
            async with self.semaphore:
                try:
                    result = await self.sandbox.commands.run(cmd)
                    return {
                        "command": cmd,
                        "exit_code": result.exit_code,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "success": result.exit_code == 0,
                    }
                except Exception as e:
                    return {"command": cmd, "error": str(e), "success": False}

        tasks = [execute_single_command(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks)

        return results


# ======================== 测试用例和示例 ========================


def demo_code_execution_service():
    """演示代码执行服务"""
    logger.info("=== 代码执行服务演示 ===")

    service = CodeExecutionService()

    # Python代码示例
    python_codes = [
        "print('Hello, World!')",
        """
import math
result = math.sqrt(16)
print(f'Square root of 16 is {result}')
        """,
        """
# 测试错误处理
try:
    x = 1 / 0
except ZeroDivisionError as e:
    print(f'Caught error: {e}')
        """,
        """
# 测试超时
import time
print('Starting long task...')
time.sleep(35)  # 这会触发超时
print('Task completed')
        """,
    ]

    for i, code in enumerate(python_codes):
        logger.info(f"执行Python代码 {i + 1}:")
        try:
            result = service.execute_python_code(code, timeout=30)
            logger.info(f"退出码: {result['exit_code']}")
            logger.info(f"输出: {result['stdout'][:200]}...")  # 只显示前200字符
            if result["stderr"]:
                logger.info(f"错误: {result['stderr'][:200]}...")
            if result["timed_out"]:
                logger.info("任务因超时被终止")
        except Exception as e:
            logger.error(f"执行失败: {e}")

        logger.info("-" * 50)


async def demo_async_code_execution_service():
    """演示异步代码执行服务"""
    logger.info("=== 异步代码执行服务演示 ===")

    service = CodeExecutionService(use_async=True)

    # 并发执行多个Python代码
    python_codes = [
        "print(f'Task 1: {2 + 2}')",
        "print(f'Task 2: {3 * 3}')",
        "import time; time.sleep(2); print('Task 3: Long running task completed')",
        "print(f'Task 4: {list(range(5))}')",
    ]

    start_time = time.time()

    # 并发执行
    tasks = [service.async_execute_python_code(code) for code in python_codes]
    results = await asyncio.gather(*tasks)

    duration = time.time() - start_time

    logger.info(f"并发执行 {len(python_codes)} 个任务，耗时: {duration:.3f}秒")

    for i, result in enumerate(results):
        logger.info(
            f"任务 {i + 1} - 退出码: {result['exit_code']}, 输出: {result['stdout'].strip()}"
        )


def demo_file_processing_service():
    """演示文件处理服务"""
    logger.info("=== 文件处理服务演示 ===")

    service = FileProcessingService()

    # 测试文件数据
    test_files = [
        {
            "name": "sample.txt",
            "content": "Hello World!\nThis is a test file.\nLine 3\nLine 4",
        },
        {
            "name": "data.json",
            "content": json.dumps(
                {"key": "value", "numbers": [1, 2, 3], "nested": {"a": 1}}
            ),
        },
        {"name": "invalid.json", "content": '{"incomplete": json'},
        {"name": "binary.bin", "content": "Binary content here"},
    ]

    try:
        results = service.process_files_batch(test_files)

        logger.info(f"处理了 {len(results)} 个文件:")
        for result in results:
            logger.info(f"  {result['name']}: {result}")

    except Exception as e:
        logger.error(f"文件处理失败: {e}")


async def demo_async_file_processing_service():
    """演示异步文件处理服务"""
    logger.info("=== 异步文件处理服务演示 ===")

    service = FileProcessingService()

    # 创建更多测试文件进行并发处理
    test_files = [
        {"name": f"test_{i}.txt", "content": f"Content of file {i}\n" * (i + 1)}
        for i in range(20)
    ]

    # 添加一些JSON文件
    for i in range(5):
        test_files.append(
            {
                "name": f"data_{i}.json",
                "content": json.dumps({"id": i, "data": list(range(i + 1))}),
            }
        )

    start_time = time.time()

    try:
        results = await service.async_process_files_batch(test_files)
        duration = time.time() - start_time

        logger.info(f"异步处理了 {len(results)} 个文件，耗时: {duration:.3f}秒")

        # 统计结果
        text_files = [r for r in results if r["type"] == "text"]
        json_files = [r for r in results if r["type"] == "json"]

        logger.info(f"文本文件: {len(text_files)}, JSON文件: {len(json_files)}")

        if text_files:
            total_lines = sum(f["lines"] for f in text_files)
            logger.info(f"总行数: {total_lines}")

        if json_files:
            valid_json = sum(1 for f in json_files if f["valid_json"])
            logger.info(f"有效JSON文件: {valid_json}/{len(json_files)}")

    except Exception as e:
        logger.error(f"异步文件处理失败: {e}")


def demo_interactive_session():
    """演示交互式会话"""
    logger.info("=== 交互式会话演示 ===")

    with SandboxManager().get_sandbox() as sandbox:
        session = InteractiveSession(sandbox)

        try:
            # 启动交互式Python
            pty = session.start_interactive_python()

            # 执行一些Python命令
            commands = [
                "x = 10",
                "y = 20",
                "print(f'x + y = {x + y}')",
                "import os",
                "print(f'Current directory: {os.getcwd()}')",
                "for i in range(3): print(f'Loop {i}')",
                "exit()",
            ]

            for cmd in commands:
                logger.info(f"执行命令: {cmd}")
                session.execute_command(cmd)
                time.sleep(1)  # 给命令一些执行时间

            # 等待Python退出
            time.sleep(3)

            # 获取会话摘要
            summary = session.get_session_summary()
            logger.info(f"会话摘要: {summary}")

        except Exception as e:
            logger.error(f"交互式会话失败: {e}")


async def demo_async_interactive_session():
    """演示异步交互式会话"""
    logger.info("=== 异步交互式会话演示 ===")

    async with AsyncSandboxManager().get_sandbox() as sandbox:
        session = InteractiveSession(sandbox)

        try:
            # 启动异步交互式Python
            pty = await session.async_start_interactive_python()

            # 异步执行Python命令
            commands = [
                "import asyncio",
                "print('Async Python session started')",
                "data = [1, 2, 3, 4, 5]",
                "result = sum(data)",
                "print(f'Sum: {result}')",
                "exit()",
            ]

            for cmd in commands:
                logger.info(f"异步执行命令: {cmd}")
                await session.async_execute_command(cmd)
                await asyncio.sleep(1)

            # 等待Python退出
            await asyncio.sleep(3)

            # 获取会话摘要
            summary = session.get_session_summary()
            logger.info(f"异步会话摘要: {summary}")

        except Exception as e:
            logger.error(f"异步交互式会话失败: {e}")


def demo_performance_optimization():
    """演示性能优化技巧"""
    logger.info("=== 性能优化演示 ===")

    with SandboxManager().get_sandbox() as sandbox:
        # 准备测试数据
        operations = []

        # 添加写操作
        for i in range(50):
            operations.append(
                {
                    "type": "write",
                    "path": f"/tmp/perf_test_{i}.txt",
                    "data": f"Performance test file {i}\n" * 10,
                }
            )

        # 添加读操作（先写入一些文件）
        for i in range(10):
            sandbox.files.write(f"/tmp/read_test_{i}.txt", f"Read test {i}")
            operations.append({"type": "read", "path": f"/tmp/read_test_{i}.txt"})

        # 测试优化的批量操作
        start_time = time.time()
        results = OptimizedFileOperations.batch_file_operations_sync(
            sandbox, operations
        )
        duration = time.time() - start_time

        logger.info(f"批量操作完成，耗时: {duration:.3f}秒")
        logger.info(f"写入文件: {len(results.get('writes', []))}")
        logger.info(f"读取文件: {len(results.get('reads', []))}")

        # 测试并发命令执行
        commands = [f"echo 'Command {i}'" for i in range(20)]

        command_pool = CommandExecutionPool(sandbox, max_concurrent=5)
        start_time = time.time()
        command_results = command_pool.execute_commands_concurrent(commands)
        duration = time.time() - start_time

        logger.info(f"并发执行 {len(commands)} 个命令，耗时: {duration:.3f}秒")
        successful_commands = sum(1 for r in command_results if r["success"])
        logger.info(f"成功执行: {successful_commands}/{len(command_results)}")


async def demo_async_performance_optimization():
    """演示异步性能优化技巧"""
    logger.info("=== 异步性能优化演示 ===")

    async with AsyncSandboxManager().get_sandbox() as sandbox:
        # 准备测试数据
        operations = []

        # 添加写操作
        for i in range(100):  # 异步可以处理更多
            operations.append(
                {
                    "type": "write",
                    "path": f"/tmp/async_perf_test_{i}.txt",
                    "data": f"Async performance test file {i}\n" * 10,
                }
            )

        # 先写入一些文件用于读取测试
        write_ops = [
            {"path": f"/tmp/async_read_test_{i}.txt", "data": f"Async read test {i}"}
            for i in range(20)
        ]
        await sandbox.files.write(write_ops)

        # 添加读操作
        for i in range(20):
            operations.append({"type": "read", "path": f"/tmp/async_read_test_{i}.txt"})

        # 测试异步优化的批量操作
        start_time = time.time()
        results = await OptimizedFileOperations.batch_file_operations_async(
            sandbox, operations
        )
        duration = time.time() - start_time

        logger.info(f"异步批量操作完成，耗时: {duration:.3f}秒")
        logger.info(f"写入文件: {len(results.get('writes', []))}")
        logger.info(f"读取文件: {len(results.get('reads', []))}")

        # 测试异步并发命令执行
        commands = [f"echo 'Async Command {i}'" for i in range(50)]

        command_pool = AsyncCommandExecutionPool(sandbox, max_concurrent=10)
        start_time = time.time()
        command_results = await command_pool.execute_commands_concurrent(commands)
        duration = time.time() - start_time

        logger.info(f"异步并发执行 {len(commands)} 个命令，耗时: {duration:.3f}秒")
        successful_commands = sum(1 for r in command_results if r["success"])
        logger.info(f"成功执行: {successful_commands}/{len(command_results)}")


# ======================== 主测试函数 ========================


def run_sync_examples():
    """运行同步示例"""
    logger.info("开始运行同步沙箱使用示例...")

    try:
        demo_code_execution_service()
        demo_file_processing_service()
        demo_interactive_session()
        demo_performance_optimization()
    except Exception as e:
        logger.error(f"同步示例执行失败: {e}")


async def run_async_examples():
    """运行异步示例"""
    logger.info("开始运行异步沙箱使用示例...")

    try:
        await demo_async_code_execution_service()
        await demo_async_file_processing_service()
        await demo_async_interactive_session()
        await demo_async_performance_optimization()
    except Exception as e:
        logger.error(f"异步示例执行失败: {e}")


def main():
    """主函数"""
    logger.info("沙箱使用示例和最佳实践演示")
    logger.info("=" * 60)

    # 运行同步示例
    run_sync_examples()

    logger.info("\n" + "=" * 60)

    # 运行异步示例
    asyncio.run(run_async_examples())

    logger.info("\n所有示例运行完成!")


if __name__ == "__main__":
    main()
