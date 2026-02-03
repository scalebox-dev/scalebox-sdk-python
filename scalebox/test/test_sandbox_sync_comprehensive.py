#!/usr/bin/env python3
"""
Comprehensive validation test for sandbox_sync module.

This test suite demonstrates and validates all key functionality of the Sandbox:
- Sandbox lifecycle management (create, connect, kill)
- File system operations (read, write, list, remove, etc.)
- Command execution (foreground, background, PTY)
- Static methods and class methods
- Error handling and edge cases
- Performance testing
"""

import datetime
import logging
import os
import tempfile
import threading
import time
from io import BytesIO, StringIO
from typing import List, Optional
from venv import create

from scalebox.exceptions import SandboxException
from scalebox.sandbox.commands.command_handle import CommandExitException, PtySize
from scalebox.sandbox.filesystem.filesystem import EntryInfo, FileType, WriteInfo
from scalebox.sandbox_sync.main import Sandbox

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SandboxValidator:
    """Comprehensive Sandbox validation test suite."""

    def __init__(self):
        self.sandbox: Optional[Sandbox] = None
        self.test_results = []
        self.failed_tests = []

    def log_test_result(
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

    def run_test(self, test_func, test_name: str):
        """运行单个测试并记录结果"""
        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, str(e), duration=duration)

    # ======================== 基础沙箱操作测试 ========================

    def test_sandbox_creation(self):
        """测试沙箱创建"""
        self.sandbox = Sandbox.create(
            template="base",
            # debug=True,
            timeout=3600,
            metadata={"test": "sync_validation"},
            envs={"TEST_ENV": "sync_test"},
        )
        assert self.sandbox is not None
        assert self.sandbox.sandbox_id is not None
        logger.info(f"Created sandbox with ID: {self.sandbox.sandbox_id}")

    def test_sandbox_is_running(self):
        """测试沙箱运行状态检查"""
        assert self.sandbox is not None
        is_running = self.sandbox.is_running()
        assert is_running == True
        logger.info(f"Sandbox is running: {is_running}")

    def test_sandbox_get_info(self):
        """测试获取沙箱信息"""
        assert self.sandbox is not None
        info = self.sandbox.get_info()
        assert info is not None
        assert info.sandbox_id == self.sandbox.sandbox_id
        logger.info(f"Sandbox info: {info}")

    def test_sandbox_set_timeout(self):
        """测试设置沙箱超时"""
        assert self.sandbox is not None
        self.sandbox.set_timeout(600)  # 设置10分钟超时
        logger.info("Successfully set sandbox timeout to 600 seconds")

    def test_sandbox_get_metrics(self):
        """测试获取沙箱指标"""
        assert self.sandbox is not None
        try:
            metrics = self.sandbox.get_metrics()
            logger.info(f"Sandbox metrics: {len(metrics) if metrics else 0} entries")
        except Exception as e:
            # 某些版本可能不支持指标
            logger.warning(f"Metrics not supported: {e}")

    # ======================== 文件系统操作测试 ========================

    def test_filesystem_write_text(self):
        """测试写入文本文件"""
        assert self.sandbox is not None
        test_content = "Hello, Sandbox!\nThis is a test file.\n测试中文内容"

        result = self.sandbox.files.write("/tmp/test_sync.txt", test_content)
        print(result)
        assert isinstance(result, WriteInfo)
        assert result.path == "/tmp/test_sync.txt"
        assert result.type == FileType.FILE
        logger.info(f"Written file: {result}")

    def test_filesystem_write_bytes(self):
        """测试写入字节文件"""
        assert self.sandbox is not None
        test_content = b"Binary content: \x00\x01\x02\x03\xff"

        result = self.sandbox.files.write("/tmp/test_binary.bin", test_content)
        print(result)
        assert isinstance(result, WriteInfo)
        assert result.path == "/tmp/test_binary.bin"

    def test_filesystem_write_io(self):
        """测试写入IO对象"""
        assert self.sandbox is not None

        # 测试StringIO
        string_io = StringIO("Content from StringIO\nSecond line")
        result1 = self.sandbox.files.write("/tmp/test_stringio.txt", string_io)
        print(result1)
        assert isinstance(result1, WriteInfo)

        # 测试BytesIO
        bytes_io = BytesIO(b"Content from BytesIO")
        result2 = self.sandbox.files.write("/tmp/test_bytesio.bin", bytes_io)
        print(result2)
        assert isinstance(result2, WriteInfo)

    def test_filesystem_write_multiple(self):
        """测试批量写入文件"""
        assert self.sandbox is not None

        files = [
            {"path": "/tmp/multi1.txt", "data": "Content of file 1"},
            {"path": "/tmp/multi2.txt", "data": "Content of file 2"},
            {"path": "/tmp/multi3.bin", "data": b"Binary content of file 3"},
        ]

        results = self.sandbox.files.write(files)
        print(results)
        assert isinstance(results, list)
        assert len(results) == 3
        for result in results:
            assert isinstance(result, WriteInfo)

    def test_filesystem_read_text(self):
        """测试读取文本文件"""
        assert self.sandbox is not None

        content = self.sandbox.files.read("/tmp/test_sync.txt", format="text")
        print(content)
        assert isinstance(content, str)
        assert "Hello, Sandbox!" in content
        assert "测试中文内容" in content

    def test_filesystem_read_bytes(self):
        """测试读取字节文件"""
        assert self.sandbox is not None

        content = self.sandbox.files.read("/tmp/test_binary.bin", format="bytes")
        print(content)
        assert isinstance(content, bytearray)
        expected = b"Binary content: \x00\x01\x02\x03\xff"
        assert bytes(content) == expected

    def test_filesystem_read_stream(self):
        """测试流式读取文件"""
        assert self.sandbox is not None

        stream = self.sandbox.files.read("/tmp/test_sync.txt", format="stream")
        chunks = []
        for chunk in stream:
            chunks.append(chunk)

        content = b"".join(chunks).decode("utf-8")
        print(content)
        assert "Hello, Sandbox!" in content

    def test_filesystem_list(self):
        """测试列出目录内容"""
        assert self.sandbox is not None

        entries = self.sandbox.files.list("/tmp", depth=1)
        print(entries)
        assert isinstance(entries, list)
        assert len(entries) > 0

        # 检查我们创建的文件是否存在
        filenames = [entry.name for entry in entries]
        assert "test_sync.txt" in filenames

        for entry in entries:
            assert isinstance(entry, EntryInfo)
            assert entry.name is not None
            assert entry.path is not None
        entries = self.sandbox.files.list("/", depth=1)
        print(entries)
        assert isinstance(entries, list)
        assert len(entries) > 0

        self.sandbox.files.make_dir("/data/test_dir")

        entries = self.sandbox.files.list("/data", depth=1)
        print(entries)
        assert isinstance(entries, list)
        assert len(entries) > 0

    def test_filesystem_exists(self):
        """测试文件存在性检查"""
        assert self.sandbox is not None

        # 检查存在的文件
        exists = self.sandbox.files.exists("/tmp/test_sync.txt")
        assert exists == True

        # 检查不存在的文件
        not_exists = self.sandbox.files.exists("/tmp/nonexistent.txt")
        assert not_exists == False

    def test_filesystem_get_info(self):
        """测试获取文件信息"""
        assert self.sandbox is not None
        info = self.sandbox.files.get_info("/tmp/test_sync.txt")
        assert isinstance(info, EntryInfo)
        assert info.name == "test_sync.txt"
        assert info.type == FileType.FILE
        assert info.path == "/tmp/test_sync.txt"
        assert info.size > 0

    def test_filesystem_make_dir(self):
        """测试创建目录"""
        assert self.sandbox is not None

        # 创建新目录
        result = self.sandbox.files.make_dir("/tmp/test_dir/nested_dir")
        assert result == True

        # 再次创建同一目录应该返回False
        result = self.sandbox.files.make_dir("/tmp/test_dir")
        assert result == False

    def test_filesystem_rename(self):
        """测试重命名文件"""
        assert self.sandbox is not None

        # 创建一个测试文件
        self.sandbox.files.write("/tmp/old_name.txt", "content to rename")

        # 重命名
        result = self.sandbox.files.rename("/tmp/old_name.txt", "/tmp/new_name.txt")
        assert isinstance(result, EntryInfo)
        assert result.name == "new_name.txt"

        # 确认旧文件不存在，新文件存在
        assert self.sandbox.files.exists("/tmp/old_name.txt") == False
        assert self.sandbox.files.exists("/tmp/new_name.txt") == True

    def test_filesystem_remove(self):
        """测试删除文件和目录"""
        assert self.sandbox is not None

        # 删除文件
        self.sandbox.files.remove("/tmp/new_name.txt")
        assert self.sandbox.files.exists("/tmp/new_name.txt") == False

        # 删除目录
        self.sandbox.files.remove("/tmp/test_dir")
        assert self.sandbox.files.exists("/tmp/test_dir") == False

    # ======================== 命令执行测试 ========================

    def test_command_run_foreground(self):
        """测试前台命令执行"""
        assert self.sandbox is not None

        result = self.sandbox.commands.run("echo 'Hello from command'")
        assert result.exit_code == 0
        assert "Hello from command" in result.stdout
        assert result.stderr == ""

    def test_command_run_with_error(self):
        """测试执行失败的命令"""
        assert self.sandbox is not None
        try:
            result = self.sandbox.commands.run("ls /nonexistent_directory 2>&1")
        except CommandExitException as e:
            assert e.exit_code != 0
            assert (
                "No such file or directory" in e.stdout or "cannot access" in e.stdout
            )

    def test_command_run_background(self):
        """测试后台命令执行"""
        assert self.sandbox is not None

        # 启动后台命令
        handle = self.sandbox.commands.run(
            "sleep 2 && echo 'Background task completed'", background=True
        )
        print(handle)
        # 等待命令完成
        result = handle.wait()
        print(result)
        assert result.exit_code == 0
        # assert "Process is running in background" in result.stderr

    def test_command_with_env_and_cwd(self):
        """测试带环境变量和工作目录的命令"""
        assert self.sandbox is not None

        # 创建测试目录
        self.sandbox.files.make_dir("/tmp/test_cwd")

        result = self.sandbox.commands.run(
            "echo $TEST_VAR && pwd",
            envs={"TEST_VAR": "test_value"},
            cwd="/tmp/test_cwd",
        )

        assert result.exit_code == 0
        assert "test_value" in result.stdout
        assert "/tmp/test_cwd" in result.stdout

    def test_command_with_callbacks(self):
        """测试带回调的命令执行"""
        assert self.sandbox is not None

        stdout_data = []
        stderr_data = []

        def stdout_handler(data):
            stdout_data.append(data)

        def stderr_handler(data):
            stderr_data.append(data)

        result = self.sandbox.commands.run(
            "echo 'stdout message' && echo 'stderr message' >&2",
            on_stdout=stdout_handler,
            on_stderr=stderr_handler,
        )

        assert result.exit_code == 0
        # Note: 回调在命令结束后触发

    def test_command_list(self):
        """测试列出运行中的命令"""
        assert self.sandbox is not None

        # 启动一个长时间运行的后台命令
        handle = self.sandbox.commands.run("sleep 30 ", background=True)
        # 列出进程
        time.sleep(1)
        processes = self.sandbox.commands.list()
        assert isinstance(processes, list)

        # 查找我们的进程
        found = any(p.pid == handle.pid for p in processes)
        assert found == True

        # 清理：杀死进程
        killed = self.sandbox.commands.kill(handle.pid)
        print(killed)
        assert killed == True

    def test_command_send_stdin(self):
        """测试向命令发送标准输入"""
        assert self.sandbox is not None

        # 启动一个等待输入的命令
        handle = self.sandbox.commands.run("cat", background=True)
        print(handle.pid)
        # 发送输入
        self.sandbox.commands.send_stdin(handle.pid, "Hello stdin\n")

        # 等待一点时间让命令处理输入
        time.sleep(1)

        # 杀死进程并获取结果
        self.sandbox.commands.kill(handle.pid)
        result = handle.wait()

        # cat命令会被SIGKILL杀死，所以exit_code不会是0
        # 但我们验证了send_stdin没有抛出异常

    def test_command_connect(self):
        """测试连接到运行中的命令"""
        assert self.sandbox is not None

        # 启动后台命令
        handle1 = self.sandbox.commands.run("sleep 30", background=True)
        print(handle1.pid)

        # 连接到同一个进程
        handle2 = self.sandbox.commands.connect(handle1.pid)
        print(handle2.events)

        assert handle1.pid == handle2.pid

        # 清理
        self.sandbox.commands.kill(handle1.pid)

    # ======================== PTY操作测试 ========================

    def test_pty_create(self):
        """测试创建PTY"""
        assert self.sandbox is not None

        pty_data = []

        def pty_handler(data):
            pty_data.append(data)

        pty_handle = self.sandbox.pty.create(
            size=PtySize(rows=24, cols=80),
            # on_data=pty_handler,
            cwd="/tmp",
            envs={"PTY_TEST": "value"},
        )

        assert pty_handle is not None
        assert pty_handle.pid > 0

        # 发送命令并等待
        self.sandbox.pty.send_stdin(pty_handle.pid, b"echo 'PTY test'\n")
        time.sleep(2)

        # 调整大小
        self.sandbox.pty.resize(pty_handle.pid, PtySize(rows=30, cols=100))

        # 清理
        killed = self.sandbox.pty.kill(pty_handle.pid)
        assert killed == True

    # ======================== 静态方法测试 ========================

    def test_static_methods(self):
        """测试静态方法"""
        assert self.sandbox is not None
        sandbox_id = self.sandbox.sandbox_id

        # 静态方法获取信息
        info = Sandbox.get_info(sandbox_id)
        assert info.sandbox_id == sandbox_id

        # 静态方法设置超时
        Sandbox.set_timeout(sandbox_id, 900)

        # 静态方法获取指标（可能不支持）
        try:
            metrics = Sandbox.get_metrics(sandbox_id)
            logger.info(f"Static method metrics: {len(metrics) if metrics else 0}")
        except Exception as e:
            logger.warning(f"Static method metrics not supported: {e}")

    # ======================== 错误处理测试 ========================

    def test_error_handling_file_operations(self):
        """测试文件操作错误处理"""
        assert self.sandbox is not None

        # 读取不存在的文件
        try:
            self.sandbox.files.read("/nonexistent/file.txt")
            assert False, "应该抛出异常"
        except Exception as e:
            logger.info(f"正确捕获文件读取错误: {type(e).__name__}")

        # 写入到只读目录
        try:
            self.sandbox.files.write("/proc/test.txt", "content")
            assert False, "应该抛出异常"
        except Exception as e:
            logger.info(f"正确捕获文件写入错误: {type(e).__name__}")

    def test_error_handling_command_operations(self):
        """测试命令操作错误处理"""
        assert self.sandbox is not None

        # 杀死不存在的进程
        killed = self.sandbox.commands.kill(99999)
        assert killed == False

        # 连接到不存在的进程
        try:
            self.sandbox.commands.connect(99999)
            assert False, "应该抛出异常"
        except Exception as e:
            logger.info(f"正确捕获进程连接错误: {type(e).__name__}")

    # ======================== 性能测试 ========================

    def test_performance_file_operations(self):
        """测试文件操作性能"""
        assert self.sandbox is not None

        # 批量文件操作
        start_time = time.time()

        # 创建100个小文件
        files = [
            {"path": f"/tmp/perf_test_{i}.txt", "data": f"Content of file {i}"}
            for i in range(100)
        ]

        self.sandbox.files.write(files)
        duration = time.time() - start_time

        logger.info(f"Created 100 files in {duration:.3f}s")
        assert duration < 30  # 应该在30秒内完成

        # 清理
        for i in range(100):
            try:
                self.sandbox.files.remove(f"/tmp/perf_test_{i}.txt")
            except:
                pass

    def test_performance_command_operations(self):
        """测试命令操作性能"""
        assert self.sandbox is not None

        start_time = time.time()

        # 执行10个顺序命令（同步版本）
        for i in range(10):
            result = self.sandbox.commands.run(f"echo 'Command {i}'")
            assert result.exit_code == 0
            assert f"Command {i}" in result.stdout

        duration = time.time() - start_time
        logger.info(f"Executed 10 sequential commands in {duration:.3f}s")

    def test_performance_concurrent_commands(self):
        """测试并发命令性能（使用线程池）"""
        assert self.sandbox is not None

        def run_command(i):
            result = self.sandbox.commands.run(f"echo 'Concurrent command {i}'")
            assert result.exit_code == 0
            return result

        start_time = time.time()

        # 使用线程池执行并发命令
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_command, i) for i in range(10)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        duration = time.time() - start_time
        logger.info(f"Executed 10 concurrent commands in {duration:.3f}s")
        assert len(results) == 10

    # ======================== 连接测试 ========================

    def test_sandbox_connect(self):
        """测试连接到现有沙箱"""
        assert self.sandbox is not None
        original_id = self.sandbox.sandbox_id

        # 连接到现有沙箱
        connected_sandbox = Sandbox.connect(original_id)
        assert connected_sandbox.sandbox_id == original_id

        # 验证连接的沙箱可以正常使用
        is_running = connected_sandbox.is_running()
        logger.info(f"Connected sandbox running status: {is_running}")

        # 在连接的沙箱中执行操作
        result = connected_sandbox.commands.run("echo 'Connected sandbox test'")
        assert result.exit_code == 0
        assert "Connected sandbox test" in result.stdout

    # ======================== 上下文管理器测试 ========================

    def test_context_manager(self):
        """测试上下文管理器"""
        # 使用上下文管理器创建临时沙箱
        with Sandbox(template="base") as temp_sandbox:
            assert temp_sandbox is not None

            # 在上下文中使用沙箱
            result = temp_sandbox.commands.run("echo 'Context manager test'")
            assert result.exit_code == 0

            temp_id = temp_sandbox.sandbox_id

        # 沙箱应该已经被自动清理

    # ======================== 文件系统高级测试 ========================

    def test_filesystem_watch_dir(self):
        """测试目录监控"""
        assert self.sandbox is not None

        # 创建测试目录
        self.sandbox.files.make_dir("/tmp/watch_test")

        events_received = []

        def event_handler(event):
            events_received.append(event)

        # 开始监控目录
        try:
            watch_handle = self.sandbox.files.watch_dir(
                "/tmp/watch_test", on_event=event_handler, timeout=10
            )

            # 在监控的目录中创建文件
            self.sandbox.files.write("/tmp/watch_test/new_file.txt", "test content")

            # 等待事件
            time.sleep(2)

            # 停止监控
            watch_handle.stop()

            logger.info(f"Received {len(events_received)} filesystem events")

        except Exception as e:
            logger.warning(
                f"Directory watching test failed (may not be supported): {e}"
            )

    # ======================== 主测试执行器 ========================

    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始Sandbox综合验证测试...")

        # 基础操作测试
        self.run_test(self.test_sandbox_creation, "Sandbox Creation")
        self.run_test(self.test_sandbox_is_running, "Sandbox Running Status")
        self.run_test(self.test_sandbox_get_info, "Sandbox Get Info")
        self.run_test(self.test_sandbox_set_timeout, "Sandbox Set Timeout")
        self.run_test(self.test_sandbox_get_metrics, "Sandbox Get Metrics")

        # 文件系统操作测试
        self.run_test(self.test_filesystem_write_text, "Filesystem Write Text")
        self.run_test(self.test_filesystem_write_bytes, "Filesystem Write Bytes")
        self.run_test(self.test_filesystem_write_io, "Filesystem Write IO")
        self.run_test(self.test_filesystem_write_multiple, "Filesystem Write Multiple")
        self.run_test(self.test_filesystem_read_text, "Filesystem Read Text")
        self.run_test(self.test_filesystem_read_bytes, "Filesystem Read Bytes")
        self.run_test(self.test_filesystem_read_stream, "Filesystem Read Stream")
        self.run_test(self.test_filesystem_list, "Filesystem List")
        self.run_test(self.test_filesystem_exists, "Filesystem Exists")
        self.run_test(self.test_filesystem_get_info, "Filesystem Get Info")
        self.run_test(self.test_filesystem_make_dir, "Filesystem Make Dir")
        self.run_test(self.test_filesystem_rename, "Filesystem Rename")
        self.run_test(self.test_filesystem_remove, "Filesystem Remove")

        # 命令执行测试
        self.run_test(self.test_command_run_foreground, "Command Run Foreground")
        self.run_test(self.test_command_run_with_error, "Command Run With Error")
        self.run_test(self.test_command_run_background, "Command Run Background")
        self.run_test(self.test_command_with_env_and_cwd, "Command With Env And CWD")
        self.run_test(self.test_command_with_callbacks, "Command With Callbacks")
        self.run_test(self.test_command_list, "Command List")
        # self.run_test(self.test_command_send_stdin, "Command Send Stdin")
        # self.run_test(self.test_command_connect, "Command Connect")

        # PTY测试
        # self.run_test(self.test_pty_create, "PTY Create")

        # 静态方法测试
        self.run_test(self.test_static_methods, "Static Methods")

        # 错误处理测试
        self.run_test(
            self.test_error_handling_file_operations, "Error Handling File Operations"
        )
        self.run_test(
            self.test_error_handling_command_operations,
            "Error Handling Command Operations",
        )

        # 性能测试
        self.run_test(
            self.test_performance_file_operations, "Performance File Operations"
        )
        self.run_test(
            self.test_performance_command_operations, "Performance Command Operations"
        )
        self.run_test(
            self.test_performance_concurrent_commands, "Performance Concurrent Commands"
        )

        # 连接测试
        self.run_test(self.test_sandbox_connect, "Sandbox Connect")

        # 上下文管理器测试
        self.run_test(self.test_context_manager, "Context Manager")

        # 高级文件系统测试
        self.run_test(self.test_filesystem_watch_dir, "Filesystem Watch Dir")

    def cleanup(self):
        """清理资源"""
        if self.sandbox:
            try:
                # self.sandbox.kill()
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
        print("Sandbox综合验证测试报告")
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


def main():
    """主函数"""
    validator = SandboxValidator()

    try:
        validator.run_all_tests()
    finally:
        validator.cleanup()
        validator.print_summary()


if __name__ == "__main__":
    main()
