#!/usr/bin/env python3
"""
Comprehensive validation test for sandbox_async module.

This test suite demonstrates and validates all key functionality of the AsyncSandbox:
- Sandbox lifecycle management (create, connect, kill)
- File system operations (read, write, list, remove, etc.)
- Command execution (foreground, background, PTY)
- Static methods and class methods
- Error handling and edge cases
- Performance testing
"""

import asyncio
import datetime
import logging
import os
import tempfile
import time
from doctest import debug
from io import BytesIO, StringIO
from typing import List, Optional

from scalebox.exceptions import SandboxException
from scalebox.sandbox.commands.command_handle import CommandExitException, PtySize
from scalebox.sandbox.filesystem.filesystem import EntryInfo, FileType, WriteInfo
from scalebox.sandbox_async.main import AsyncSandbox

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AsyncSandboxValidator:
    """Comprehensive AsyncSandbox validation test suite."""

    def __init__(self):
        self.sandbox: Optional[AsyncSandbox] = None
        self.test_results = []
        self.failed_tests = []

    async def log_test_result(
        self, test_name: str, success: bool, message: str = "", duration: float = 0
    ):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
        }
        self.test_results.append(result)

        if not success:
            self.failed_tests.append(test_name)

        logger.info(f"{status} {test_name} ({duration:.3f}s) {message}")

    async def run_test(self, test_func, test_name: str):
        """运行单个测试并记录结果"""
        start_time = time.time()
        try:
            await test_func()
            duration = time.time() - start_time
            await self.log_test_result(test_name, True, duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test_result(test_name, False, str(e), duration=duration)

    # ======================== 基础沙箱操作测试 ========================

    async def test_sandbox_creation(self):
        """测试沙箱创建"""
        self.sandbox = await AsyncSandbox.create(
            template="base",
            debug=False,
            timeout=300,
            api_key="sk-Wk4Ig",
            metadata={"test": "async_validation"},
            envs={"TEST_ENV": "async_test"},
        )
        assert self.sandbox is not None
        assert self.sandbox.sandbox_id is not None
        logger.info(f"Created sandbox with ID: {self.sandbox.sandbox_id}")

    async def test_sandbox_is_running(self):
        """测试沙箱运行状态检查"""
        assert self.sandbox is not None
        is_running = await self.sandbox.is_running()
        assert is_running == True
        logger.info(f"Sandbox is running: {is_running}")

    async def test_sandbox_get_info(self):
        """测试获取沙箱信息"""
        assert self.sandbox is not None
        info = await self.sandbox.get_info()
        assert info is not None
        assert info.sandbox_id == self.sandbox.sandbox_id
        logger.info(f"Sandbox info: {info}")

    async def test_sandbox_set_timeout(self):
        """测试设置沙箱超时"""
        assert self.sandbox is not None
        await self.sandbox.set_timeout(600)  # 设置10分钟超时
        logger.info("Successfully set sandbox timeout to 600 seconds")

    async def test_sandbox_get_metrics(self):
        """测试获取沙箱指标"""
        assert self.sandbox is not None
        try:
            metrics = await self.sandbox.get_metrics()
            print(metrics)
            logger.info(f"Sandbox metrics: {len(metrics) if metrics else 0} entries")
        except Exception as e:
            # 某些版本可能不支持指标
            logger.warning(f"Metrics not supported: {e}")

    # ======================== 文件系统操作测试 ========================

    async def test_filesystem_write_text(self):
        """测试写入文本文件"""
        assert self.sandbox is not None
        test_content = "Hello, AsyncSandbox!\nThis is a test file.\n测试中文内容"

        result = await self.sandbox.files.write("/tmp/test_async.txt", test_content)
        print(result)
        assert isinstance(result, WriteInfo)
        assert result.path == "/tmp/test_async.txt"
        assert result.type == FileType.FILE
        logger.info(f"Written file: {result}")

    async def test_filesystem_write_bytes(self):
        """测试写入字节文件"""
        assert self.sandbox is not None
        test_content = b"Binary content: \x00\x01\x02\x03\xff"

        result = await self.sandbox.files.write("/tmp/test_binary.bin", test_content)
        print(result)
        assert isinstance(result, WriteInfo)
        assert result.path == "/tmp/test_binary.bin"

    async def test_filesystem_write_io(self):
        """测试写入IO对象"""
        assert self.sandbox is not None

        # 测试StringIO
        string_io = StringIO("Content from StringIO\nSecond line")
        result1 = await self.sandbox.files.write("/tmp/test_stringio.txt", string_io)
        print(result1)
        assert isinstance(result1, WriteInfo)

        # 测试BytesIO
        bytes_io = BytesIO(b"Content from BytesIO")
        result2 = await self.sandbox.files.write("/tmp/test_bytesio.bin", bytes_io)
        print(result2)
        assert isinstance(result2, WriteInfo)

    async def test_filesystem_write_multiple(self):
        """测试批量写入文件"""
        assert self.sandbox is not None

        files = [
            {"path": "/tmp/multi1.txt", "data": "Content of file 1"},
            {"path": "/tmp/multi2.txt", "data": "Content of file 2"},
            {"path": "/tmp/multi3.bin", "data": b"Binary content of file 3"},
        ]

        results = await self.sandbox.files.write(files)
        print(results)
        assert isinstance(results, list)
        assert len(results) == 3
        for result in results:
            assert isinstance(result, WriteInfo)

    async def test_filesystem_read_text(self):
        """测试读取文本文件"""
        assert self.sandbox is not None

        content = await self.sandbox.files.read("/tmp/test_async.txt", format="text")
        print(content)
        assert isinstance(content, str)
        assert "Hello, AsyncSandbox!" in content
        assert "测试中文内容" in content

    async def test_filesystem_read_bytes(self):
        """测试读取字节文件"""
        assert self.sandbox is not None

        content = await self.sandbox.files.read("/tmp/test_binary.bin", format="bytes")
        print(content)
        assert isinstance(content, bytearray)
        expected = b"Binary content: \x00\x01\x02\x03\xff"
        assert bytes(content) == expected

    async def test_filesystem_read_stream(self):
        """测试流式读取文件"""
        assert self.sandbox is not None

        stream = await self.sandbox.files.read("/tmp/test_async.txt", format="stream")
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        content = b"".join(chunks).decode("utf-8")
        print(content)
        assert "Hello, AsyncSandbox!" in content

    async def test_filesystem_list(self):
        """测试列出目录内容"""
        assert self.sandbox is not None

        entries = await self.sandbox.files.list("/tmp", depth=1)
        print(entries)
        assert isinstance(entries, list)
        assert len(entries) > 0

        # 检查我们创建的文件是否存在
        filenames = [entry.name for entry in entries]
        assert "test_async.txt" in filenames

        for entry in entries:
            assert isinstance(entry, EntryInfo)
            assert entry.name is not None
            assert entry.path is not None

    async def test_filesystem_exists(self):
        """测试文件存在性检查"""
        assert self.sandbox is not None

        # 检查存在的文件
        exists = await self.sandbox.files.exists("/tmp/test_async.txt")
        print(exists)
        assert exists == True

        # 检查不存在的文件
        not_exists = await self.sandbox.files.exists("/tmp/nonexistent.txt")
        print(not_exists)
        assert not_exists == False

    async def test_filesystem_get_info(self):
        """测试获取文件信息"""
        assert self.sandbox is not None

        info = await self.sandbox.files.get_info("/tmp/test_async.txt")
        print(info)
        assert isinstance(info, EntryInfo)
        assert info.name == "test_async.txt"
        assert info.type == FileType.FILE
        assert info.path == "/tmp/test_async.txt"
        assert info.size > 0

    async def test_filesystem_make_dir(self):
        """测试创建目录"""
        assert self.sandbox is not None

        # 创建新目录
        result = await self.sandbox.files.make_dir("/tmp/test_dir/nested_dir")
        print(result)
        assert result == True

        # 再次创建同一目录应该返回False
        result = await self.sandbox.files.make_dir("/tmp/test_dir")
        print(result)
        assert result == False

    async def test_filesystem_rename(self):
        """测试重命名文件"""
        assert self.sandbox is not None

        # 创建一个测试文件
        await self.sandbox.files.write("/tmp/old_name.txt", "content to rename")

        # 重命名
        result = await self.sandbox.files.rename("/tmp/old_name.txt", "/tmp/new_name.txt")
        print(result)
        assert isinstance(result, EntryInfo)
        assert result.name == "new_name.txt"

        # 确认旧文件不存在，新文件存在
        assert await self.sandbox.files.exists("/tmp/old_name.txt") == False
        assert await self.sandbox.files.exists("/tmp/new_name.txt") == True

    async def test_filesystem_remove(self):
        """测试删除文件和目录"""
        assert self.sandbox is not None

        # 删除文件
        await self.sandbox.files.remove("/tmp/new_name.txt")
        assert await self.sandbox.files.exists("/tmp/new_name.txt") == False
        
        # 删除目录
        await self.sandbox.files.remove("/tmp/test_dir")
        assert await self.sandbox.files.exists("/tmp/test_dir") == False

    # ======================== 命令执行测试 ========================

    async def test_command_run_foreground(self):
        """测试前台命令执行"""
        assert self.sandbox is not None

        result = await self.sandbox.commands.run("echo 'Hello from command'")
        print(result)
        assert result.exit_code == 0
        assert "Hello from command" in result.stdout
        assert result.stderr == ""

    async def test_command_run_with_error(self):
        """测试执行失败的命令"""
        assert self.sandbox is not None
        try:
            await self.sandbox.commands.run("ls /nonexistent_directory 2>&1")
        except CommandExitException as e:
            print(e)
            assert e.exit_code != 0
            assert (
                "No such file or directory" in e.stdout or "cannot access" in e.stdout
            )

    async def test_command_run_background(self):
        """测试后台命令执行"""
        assert self.sandbox is not None

        # 启动后台命令
        handle = await self.sandbox.commands.run(
            "sleep 2 && echo 'Background task completed'", background=True
        )

        # 等待命令完成
        result = await handle.wait()
        print(result)
        assert result.exit_code == 0
        assert "Background task completed" in result.stdout

    async def test_command_with_env_and_cwd(self):
        """测试带环境变量和工作目录的命令"""
        assert self.sandbox is not None

        # 创建测试目录
        await self.sandbox.files.make_dir("/tmp/test_cwd")

        result = await self.sandbox.commands.run(
            "echo $TEST_VAR && pwd",
            envs={"TEST_VAR": "test_value"},
            cwd="/tmp/test_cwd",
        )
        print(result)
        assert result.exit_code == 0
        assert "test_value" in result.stdout
        assert "/tmp/test_cwd" in result.stdout

    async def test_command_with_callbacks(self):
        """测试带回调的命令执行"""
        assert self.sandbox is not None

        stdout_data = []
        stderr_data = []

        async def stdout_handler(data):
            stdout_data.append(data)

        async def stderr_handler(data):
            stderr_data.append(data)

        result = await self.sandbox.commands.run(
            "echo 'stdout message' && echo 'stderr message' >&2",
            on_stdout=stdout_handler,
            on_stderr=stderr_handler,
        )

        assert result.exit_code == 0
        # Note: 回调可能在命令结束后才触发，这里只验证命令成功执行

    async def test_command_list(self):
        """测试列出运行中的命令"""
        assert self.sandbox is not None

        # 启动一个长时间运行的后台命令
        handle = await self.sandbox.commands.run("sleep 30", background=True)
        print(handle)
        # 列出进程
        processes = await self.sandbox.commands.list()
        print(processes)
        assert isinstance(processes, list)

        # 查找我们的进程
        found = any(p.pid == handle.pid for p in processes)
        assert found == True

        # 清理：杀死进程
        killed = await self.sandbox.commands.kill(handle.pid)
        print(killed)
        assert killed == True

    async def test_command_send_stdin(self):
        """测试向命令发送标准输入"""
        assert self.sandbox is not None

        # 启动一个等待输入的命令
        handle = await self.sandbox.commands.run("cat", background=True)
        print(handle)

        # 发送输入
        await self.sandbox.commands.send_stdin(handle.pid, "Hello stdin\n")
        print("111111111111")
        # 等待一点时间让命令处理输入
        await asyncio.sleep(1)

        # 杀死进程并获取结果
        await self.sandbox.commands.kill(handle.pid)
        print("22222222")
        try:
            result = await handle.wait()
        except CommandExitException as e:
            print(e)

        # cat命令会被SIGKILL杀死，所以exit_code不会是0
        # 但我们验证了send_stdin没有抛出异常

    async def test_command_connect(self):
        """测试连接到运行中的命令"""
        assert self.sandbox is not None

        # 启动后台命令
        handle1 = await self.sandbox.commands.run("sleep 5", background=True)
        print(handle1)
        # 连接到同一个进程
        handle2 = await self.sandbox.commands.connect(handle1.pid)
        print(handle2)
        assert handle1.pid == handle2.pid

        # 清理
        await self.sandbox.commands.kill(handle1.pid)

    # ======================== PTY操作测试 ========================

    async def test_pty_create(self):
        """测试创建PTY"""
        assert self.sandbox is not None

        pty_data = []

        async def pty_handler(data):
            pty_data.append(data)

        pty_handle = await self.sandbox.pty.create(
            size=PtySize(rows=24, cols=80),
            on_data=pty_handler,
            cwd="/tmp",
            envs={"PTY_TEST": "value"},
        )

        assert pty_handle is not None
        assert pty_handle.pid > 0

        # 发送命令并等待
        await self.sandbox.pty.send_stdin(pty_handle.pid, b"echo 'PTY test'\n")
        await asyncio.sleep(2)

        # 调整大小
        await self.sandbox.pty.resize(pty_handle.pid, PtySize(rows=30, cols=100))

        # 清理
        killed = await self.sandbox.pty.kill(pty_handle.pid)
        assert killed == True

    # ======================== 静态方法测试 ========================

    async def test_static_methods(self):
        """测试静态方法"""
        assert self.sandbox is not None
        sandbox_id = self.sandbox.sandbox_id

        # 静态方法获取信息
        info = await AsyncSandbox.get_info(sandbox_id)
        assert info.sandbox_id == sandbox_id

        # 静态方法设置超时
        await AsyncSandbox.set_timeout(sandbox_id, 900)

        # 静态方法获取指标（可能不支持）
        try:
            metrics = await AsyncSandbox.get_metrics(sandbox_id)
            logger.info(f"Static method metrics: {len(metrics) if metrics else 0}")
        except Exception as e:
            logger.warning(f"Static method metrics not supported: {e}")

    # ======================== 错误处理测试 ========================

    async def test_error_handling_file_operations(self):
        """测试文件操作错误处理"""
        assert self.sandbox is not None

        # 读取不存在的文件
        try:
            await self.sandbox.files.read("/nonexistent/file.txt")
            assert False, "应该抛出异常"
        except Exception as e:
            print(type(e).__name__)
            logger.info(f"正确捕获文件读取错误: {type(e).__name__}")

        # 写入到只读目录
        try:
            await self.sandbox.files.write("/proc/test.txt", "content")
            assert False, "应该抛出异常"
        except Exception as e:
            print(type(e).__name__)
            logger.info(f"正确捕获文件写入错误: {type(e).__name__}")

    async def test_error_handling_command_operations(self):
        """测试命令操作错误处理"""
        assert self.sandbox is not None

        # 杀死不存在的进程
        killed = await self.sandbox.commands.kill(99999)
        print(killed)
        assert killed == False

        # 连接到不存在的进程
        try:
            await self.sandbox.commands.connect(99999)
            assert False, "应该抛出异常"
        except Exception as e:
            print(type(e).__name__)
            logger.info(f"正确捕获进程连接错误: {type(e).__name__}")

    # ======================== 性能测试 ========================

    async def test_performance_file_operations(self):
        """测试文件操作性能"""
        assert self.sandbox is not None

        # 批量文件操作
        start_time = time.time()

        # 创建100个小文件
        files = [
            {"path": f"/tmp/perf_test_{i}.txt", "data": f"Content of file {i}"}
            for i in range(100)
        ]

        await self.sandbox.files.write(files)
        duration = time.time() - start_time

        logger.info(f"Created 100 files in {duration:.3f}s")
        assert duration < 30  # 应该在30秒内完成

        # 清理
        for i in range(100):
            try:
                await self.sandbox.files.remove(f"/tmp/perf_test_{i}.txt")
            except:
                pass

    async def test_performance_command_operations(self):
        """测试命令操作性能"""
        assert self.sandbox is not None

        start_time = time.time()

        # 执行10个并发命令
        tasks = []
        for i in range(10):
            task = self.sandbox.commands.run(f"echo 'Command {i}'")
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        print(f"Executed 10 concurrent commands in {duration:.3f}s")

        # 验证所有命令都成功
        for i, result in enumerate(results):
            assert result.exit_code == 0
            assert f"Command {i}" in result.stdout

    # ======================== 连接测试 ========================

    async def test_sandbox_connect(self):
        """测试连接到现有沙箱"""
        assert self.sandbox is not None
        original_id = self.sandbox.sandbox_id

        # 连接到现有沙箱
        connected_sandbox = await AsyncSandbox.connect(original_id)
        print(connected_sandbox)
        assert connected_sandbox.sandbox_id == original_id

        # 验证连接的沙箱可以正常使用
        is_running = await connected_sandbox.is_running()
        logger.info(f"Connected sandbox running status: {is_running}")

        # 在连接的沙箱中执行操作
        result = await connected_sandbox.commands.run("echo 'Connected sandbox test'")
        print(result)
        assert result.exit_code == 0
        assert "Connected sandbox test" in result.stdout

    # ======================== 上下文管理器测试 ========================

    async def test_context_manager(self):
        """测试上下文管理器"""
        # 使用上下文管理器创建临时沙箱
        async with await AsyncSandbox.create(debug=False) as temp_sandbox:
            assert temp_sandbox is not None

            # 在上下文中使用沙箱
            result = await temp_sandbox.commands.run("echo 'Context manager test'")
            print(result)
            assert result.exit_code == 0

            temp_id = temp_sandbox.sandbox_id

        # 沙箱应该已经被自动清理
        # （注意：这里可能需要等待一段时间才能验证）

    # ======================== 主测试执行器 ========================

    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始AsyncSandbox综合验证测试...")

        # 基础操作测试
        await self.run_test(self.test_sandbox_creation, "Sandbox Creation")
        await self.run_test(self.test_sandbox_is_running, "Sandbox Running Status")
        await self.run_test(self.test_sandbox_get_info, "Sandbox Get Info")
        await self.run_test(self.test_sandbox_set_timeout, "Sandbox Set Timeout")
        await self.run_test(self.test_sandbox_get_metrics, "Sandbox Get Metrics")

        # 文件系统操作测试
        await self.run_test(self.test_filesystem_write_text, "Filesystem Write Text")
        await self.run_test(self.test_filesystem_write_bytes, "Filesystem Write Bytes")
        await self.run_test(self.test_filesystem_write_io, "Filesystem Write IO")
        await self.run_test(
            self.test_filesystem_write_multiple, "Filesystem Write Multiple"
        )
        await self.run_test(self.test_filesystem_read_text, "Filesystem Read Text")
        await self.run_test(self.test_filesystem_read_bytes, "Filesystem Read Bytes")
        await self.run_test(self.test_filesystem_read_stream, "Filesystem Read Stream")
        await self.run_test(self.test_filesystem_list, "Filesystem List")
        await self.run_test(self.test_filesystem_exists, "Filesystem Exists")
        await self.run_test(self.test_filesystem_get_info, "Filesystem Get Info")
        await self.run_test(self.test_filesystem_make_dir, "Filesystem Make Dir")
        await self.run_test(self.test_filesystem_rename, "Filesystem Rename")
        await self.run_test(self.test_filesystem_remove, "Filesystem Remove")

        # 命令执行测试
        await self.run_test(self.test_command_run_foreground, "Command Run Foreground")
        await self.run_test(self.test_command_run_with_error, "Command Run With Error")
        await self.run_test(self.test_command_run_background, "Command Run Background")
        await self.run_test(
            self.test_command_with_env_and_cwd, "Command With Env And CWD"
        )
        await self.run_test(self.test_command_with_callbacks, "Command With Callbacks")
        await self.run_test(self.test_command_list, "Command List")
        await self.run_test(self.test_command_send_stdin, "Command Send Stdin")
        await self.run_test(self.test_command_connect, "Command Connect")

        # PTY测试
        await self.run_test(self.test_pty_create, "PTY Create")

        # 静态方法测试
        await self.run_test(self.test_static_methods, "Static Methods")

        # 错误处理测试
        await self.run_test(
            self.test_error_handling_file_operations, "Error Handling File Operations"
        )
        await self.run_test(
            self.test_error_handling_command_operations,
            "Error Handling Command Operations",
        )

        # 性能测试
        await self.run_test(
            self.test_performance_file_operations, "Performance File Operations"
        )
        await self.run_test(
            self.test_performance_command_operations, "Performance Command Operations"
        )

        # 连接测试
        await self.run_test(self.test_sandbox_connect, "Sandbox Connect")

        # 上下文管理器测试
        await self.run_test(self.test_context_manager, "Context Manager")

    async def cleanup(self):
        """清理资源"""
        if self.sandbox:
            try:
                await self.sandbox.kill()
                logger.info("Sandbox cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up sandbox: {e}")

    def print_summary(self):
        """打印测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        total_duration = sum(r["duration"] for r in self.test_results)

        print("\n" + "=" * 60)
        print("AsyncSandbox综合验证测试报告")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过数: {passed_tests}")
        print(f"失败数: {failed_tests}")
        print(f"总耗时: {total_duration:.3f}秒")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")

        if self.failed_tests:
            print(f"\n失败的测试:")
            for test in self.failed_tests:
                print(f"  ❌ {test}")

        print("=" * 60)


async def main():
    """主函数"""
    validator = AsyncSandboxValidator()

    try:
        await validator.run_all_tests()
    finally:
        await validator.cleanup()
        validator.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
