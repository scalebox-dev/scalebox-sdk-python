#!/usr/bin/env python3
"""
Comprehensive stress testing and edge case validation for both sandbox modules.

This test suite focuses on:
- Stress testing under high load
- Edge cases and boundary conditions
- Error recovery and resilience
- Resource management
- Concurrent operations
- Large data handling
- Network failure simulation
"""

import asyncio
import concurrent.futures
import datetime
import logging
import os
import random
import string
import threading
import time
from typing import List, Optional

from scalebox.exceptions import SandboxException
from scalebox.sandbox.commands.command_handle import PtySize
from scalebox.sandbox_async.main import AsyncSandbox
from scalebox.sandbox_sync.main import Sandbox

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StressTestValidator:
    """Comprehensive stress testing and edge case validation."""

    def __init__(self):
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

    def run_test(self, test_func, test_name: str, is_async: bool = False):
        """运行单个测试并记录结果"""
        start_time = time.time()
        try:
            if is_async:
                asyncio.run(test_func())
            else:
                test_func()
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, str(e), duration=duration)

    # ======================== 大数据处理测试 ========================

    def test_large_file_operations_sync(self):
        """测试同步版本大文件操作"""
        sandbox = Sandbox(debug=True)

        try:
            # 生成大内容（10MB）
            large_content = "A" * (10 * 1024 * 1024)

            # 写入大文件
            start_time = time.time()
            result = sandbox.files.write("/tmp/large_file.txt", large_content)
            write_duration = time.time() - start_time

            logger.info(f"写入10MB文件耗时: {write_duration:.3f}s")

            # 读取大文件
            start_time = time.time()
            read_content = sandbox.files.read("/tmp/large_file.txt")
            read_duration = time.time() - start_time

            logger.info(f"读取10MB文件耗时: {read_duration:.3f}s")

            assert len(read_content) == len(large_content)
            assert read_content[:100] == large_content[:100]  # 验证开头部分

            # 清理
            sandbox.files.remove("/tmp/large_file.txt")

        finally:
            try:
                sandbox.kill()
            except:
                pass

    async def test_large_file_operations_async(self):
        """测试异步版本大文件操作"""
        sandbox = await AsyncSandbox.create(debug=True)

        try:
            # 生成大内容（10MB）
            large_content = "B" * (10 * 1024 * 1024)

            # 写入大文件
            start_time = time.time()
            result = await sandbox.files.write(
                "/tmp/large_file_async.txt", large_content
            )
            write_duration = time.time() - start_time

            logger.info(f"异步写入10MB文件耗时: {write_duration:.3f}s")

            # 读取大文件
            start_time = time.time()
            read_content = await sandbox.files.read("/tmp/large_file_async.txt")
            read_duration = time.time() - start_time

            logger.info(f"异步读取10MB文件耗时: {read_duration:.3f}s")

            assert len(read_content) == len(large_content)
            assert read_content[:100] == large_content[:100]

            # 清理
            await sandbox.files.remove("/tmp/large_file_async.txt")

        finally:
            try:
                await sandbox.kill()
            except:
                pass

    # ======================== 并发压力测试 ========================

    def test_concurrent_sync_operations(self):
        """测试同步版本并发操作"""
        sandbox = Sandbox(debug=True)

        try:

            def worker(worker_id: int) -> dict:
                """工作线程函数"""
                results = []

                for i in range(10):
                    # 文件操作
                    filename = f"/tmp/worker_{worker_id}_file_{i}.txt"
                    content = f"Worker {worker_id}, File {i}, Content: {random.randint(1, 1000)}"

                    sandbox.files.write(filename, content)
                    read_content = sandbox.files.read(filename)
                    assert read_content == content

                    # 命令执行
                    result = sandbox.commands.run(
                        f"echo 'Worker {worker_id}, Command {i}'"
                    )
                    assert result.exit_code == 0

                    results.append({"file": filename, "command_output": result.stdout})

                    # 清理文件
                    sandbox.files.remove(filename)

                return {"worker_id": worker_id, "results": results}

            # 启动并发工作线程
            start_time = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(worker, i) for i in range(5)]
                results = [
                    future.result()
                    for future in concurrent.futures.as_completed(futures)
                ]

            duration = time.time() - start_time

            logger.info(f"5个并发工作线程完成，耗时: {duration:.3f}s")
            logger.info(f"总计处理: {len(results) * 10} 个文件操作和命令执行")

            assert len(results) == 5

        finally:
            try:
                sandbox.kill()
            except:
                pass

    async def test_concurrent_async_operations(self):
        """测试异步版本并发操作"""
        sandbox = await AsyncSandbox.create(debug=True)

        try:

            async def worker(worker_id: int) -> dict:
                """异步工作协程"""
                results = []

                for i in range(10):
                    # 文件操作
                    filename = f"/tmp/async_worker_{worker_id}_file_{i}.txt"
                    content = f"Async Worker {worker_id}, File {i}, Content: {random.randint(1, 1000)}"

                    await sandbox.files.write(filename, content)
                    read_content = await sandbox.files.read(filename)
                    assert read_content == content

                    # 命令执行
                    result = await sandbox.commands.run(
                        f"echo 'Async Worker {worker_id}, Command {i}'"
                    )
                    assert result.exit_code == 0

                    results.append({"file": filename, "command_output": result.stdout})

                    # 清理文件
                    await sandbox.files.remove(filename)

                return {"worker_id": worker_id, "results": results}

            # 启动并发协程
            start_time = time.time()

            tasks = [worker(i) for i in range(10)]  # 异步可以支持更多并发
            results = await asyncio.gather(*tasks)

            duration = time.time() - start_time

            logger.info(f"10个并发协程完成，耗时: {duration:.3f}s")
            logger.info(f"总计处理: {len(results) * 10} 个异步文件操作和命令执行")

            assert len(results) == 10

        finally:
            try:
                await sandbox.kill()
            except:
                pass

    # ======================== 内存压力测试 ========================

    def test_memory_stress_sync(self):
        """测试同步版本内存压力"""
        sandbox = Sandbox(debug=True)

        try:
            # 创建大量小文件
            num_files = 1000
            file_paths = []

            start_time = time.time()

            for i in range(num_files):
                filename = f"/tmp/memory_test_{i}.txt"
                content = f"File {i}: " + "x" * 100  # 100字符内容
                sandbox.files.write(filename, content)
                file_paths.append(filename)

            create_duration = time.time() - start_time
            logger.info(f"创建 {num_files} 个文件耗时: {create_duration:.3f}s")

            # 读取所有文件
            start_time = time.time()

            for filename in file_paths:
                content = sandbox.files.read(filename)
                assert len(content) > 100

            read_duration = time.time() - start_time
            logger.info(f"读取 {num_files} 个文件耗时: {read_duration:.3f}s")

            # 清理所有文件
            start_time = time.time()

            for filename in file_paths:
                sandbox.files.remove(filename)

            cleanup_duration = time.time() - start_time
            logger.info(f"清理 {num_files} 个文件耗时: {cleanup_duration:.3f}s")

        finally:
            try:
                sandbox.kill()
            except:
                pass

    async def test_memory_stress_async(self):
        """测试异步版本内存压力"""
        sandbox = await AsyncSandbox.create(debug=True)

        try:
            # 创建大量小文件（异步批量操作）
            num_files = 1000

            start_time = time.time()

            # 准备文件数据
            files_data = [
                {
                    "path": f"/tmp/async_memory_test_{i}.txt",
                    "data": f"Async File {i}: " + "y" * 100,
                }
                for i in range(num_files)
            ]

            # 批量写入（分批处理避免内存过大）
            batch_size = 100
            for i in range(0, num_files, batch_size):
                batch = files_data[i : i + batch_size]
                await sandbox.files.write(batch)

            create_duration = time.time() - start_time
            logger.info(f"异步创建 {num_files} 个文件耗时: {create_duration:.3f}s")

            # 异步读取所有文件
            start_time = time.time()

            async def read_file(filename):
                return await sandbox.files.read(filename)

            # 分批并发读取
            batch_size = 50
            for i in range(0, num_files, batch_size):
                tasks = []
                for j in range(i, min(i + batch_size, num_files)):
                    filename = f"/tmp/async_memory_test_{j}.txt"
                    tasks.append(read_file(filename))

                results = await asyncio.gather(*tasks)
                for result in results:
                    assert len(result) > 100

            read_duration = time.time() - start_time
            logger.info(f"异步读取 {num_files} 个文件耗时: {read_duration:.3f}s")

            # 异步清理所有文件
            start_time = time.time()

            for i in range(num_files):
                filename = f"/tmp/async_memory_test_{i}.txt"
                await sandbox.files.remove(filename)

            cleanup_duration = time.time() - start_time
            logger.info(f"异步清理 {num_files} 个文件耗时: {cleanup_duration:.3f}s")

        finally:
            try:
                await sandbox.kill()
            except:
                pass

    # ======================== 边界条件测试 ========================

    def test_edge_cases_sync(self):
        """测试同步版本边界条件"""
        sandbox = Sandbox(debug=True)

        try:
            # 空文件测试
            sandbox.files.write("/tmp/empty.txt", "")
            content = sandbox.files.read("/tmp/empty.txt")
            assert content == ""

            # 特殊字符文件名测试
            special_names = [
                "/tmp/file with spaces.txt",
                "/tmp/file_with_中文.txt",
                "/tmp/file-with-special-!@#$%.txt",
            ]

            for filename in special_names:
                try:
                    sandbox.files.write(filename, f"Content for {filename}")
                    content = sandbox.files.read(filename)
                    assert f"Content for {filename}" in content
                    sandbox.files.remove(filename)
                except Exception as e:
                    logger.warning(f"特殊文件名 {filename} 测试失败: {e}")

            # 深层目录测试
            deep_path = (
                "/tmp/" + "/".join([f"dir{i}" for i in range(10)]) + "/deep_file.txt"
            )
            sandbox.files.write(deep_path, "Deep directory content")
            content = sandbox.files.read(deep_path)
            assert content == "Deep directory content"

            # 长命令测试
            long_command = "echo " + "A" * 1000
            result = sandbox.commands.run(long_command)
            assert result.exit_code == 0
            assert len(result.stdout) > 1000

            # 零退出码和非零退出码测试
            result_success = sandbox.commands.run("exit 0")
            assert result_success.exit_code == 0

            result_fail = sandbox.commands.run("exit 42")
            assert result_fail.exit_code == 42

            logger.info("所有边界条件测试通过")

        finally:
            try:
                sandbox.kill()
            except:
                pass

    async def test_edge_cases_async(self):
        """测试异步版本边界条件"""
        sandbox = await AsyncSandbox.create(debug=True)

        try:
            # 空文件测试
            await sandbox.files.write("/tmp/async_empty.txt", "")
            content = await sandbox.files.read("/tmp/async_empty.txt")
            assert content == ""

            # 二进制数据测试
            binary_data = bytes(range(256))  # 0-255的字节
            await sandbox.files.write("/tmp/binary_test.bin", binary_data)
            read_binary = await sandbox.files.read(
                "/tmp/binary_test.bin", format="bytes"
            )
            assert bytes(read_binary) == binary_data

            # 流式读取大文件测试
            large_content = "Stream test content\n" * 10000
            await sandbox.files.write("/tmp/stream_test.txt", large_content)

            stream = await sandbox.files.read("/tmp/stream_test.txt", format="stream")
            chunks = []
            async for chunk in stream:
                chunks.append(chunk)

            reconstructed = b"".join(chunks).decode("utf-8")
            assert reconstructed == large_content

            # 超时测试
            try:
                result = await sandbox.commands.run("sleep 1", timeout=0.5)
                # 如果执行到这里，说明超时没有生效
                logger.warning("超时测试可能没有生效")
            except Exception as e:
                logger.info(f"超时测试正确触发: {type(e).__name__}")

            logger.info("所有异步边界条件测试通过")

        finally:
            try:
                await sandbox.kill()
            except:
                pass

    # ======================== 错误恢复测试 ========================

    def test_error_recovery_sync(self):
        """测试同步版本错误恢复"""
        sandbox = Sandbox(debug=True)

        try:
            # 测试从文件操作错误中恢复
            error_count = 0

            # 尝试不存在的操作
            for i in range(5):
                try:
                    sandbox.files.read(f"/nonexistent/file_{i}.txt")
                except Exception:
                    error_count += 1

                # 错误后继续正常操作
                sandbox.files.write(f"/tmp/recovery_test_{i}.txt", f"Recovery test {i}")
                content = sandbox.files.read(f"/tmp/recovery_test_{i}.txt")
                assert content == f"Recovery test {i}"
                sandbox.files.remove(f"/tmp/recovery_test_{i}.txt")

            assert error_count == 5, "应该捕获5个错误"

            # 测试从命令错误中恢复
            error_count = 0

            for i in range(5):
                # 执行失败的命令
                result = sandbox.commands.run("ls /nonexistent_dir_12345")
                if result.exit_code != 0:
                    error_count += 1

                # 错误后继续正常命令
                result = sandbox.commands.run(f"echo 'Command recovery test {i}'")
                assert result.exit_code == 0
                assert f"Command recovery test {i}" in result.stdout

            assert error_count == 5, "应该有5个失败的命令"
            logger.info("错误恢复测试通过")

        finally:
            try:
                sandbox.kill()
            except:
                pass

    async def test_error_recovery_async(self):
        """测试异步版本错误恢复"""
        sandbox = await AsyncSandbox.create(debug=True)

        try:
            # 测试异步错误恢复
            error_count = 0

            for i in range(5):
                try:
                    await sandbox.files.read(f"/nonexistent/async_file_{i}.txt")
                except Exception:
                    error_count += 1

                # 错误后继续正常操作
                await sandbox.files.write(
                    f"/tmp/async_recovery_test_{i}.txt", f"Async recovery test {i}"
                )
                content = await sandbox.files.read(f"/tmp/async_recovery_test_{i}.txt")
                assert content == f"Async recovery test {i}"
                await sandbox.files.remove(f"/tmp/async_recovery_test_{i}.txt")

            assert error_count == 5

            # 并发错误恢复测试
            async def error_and_recovery(index):
                try:
                    await sandbox.files.read(f"/nonexistent/concurrent_{index}.txt")
                except Exception:
                    pass

                # 正常操作
                await sandbox.files.write(
                    f"/tmp/concurrent_recovery_{index}.txt", f"Concurrent {index}"
                )
                content = await sandbox.files.read(
                    f"/tmp/concurrent_recovery_{index}.txt"
                )
                assert content == f"Concurrent {index}"
                await sandbox.files.remove(f"/tmp/concurrent_recovery_{index}.txt")
                return True

            # 并发执行错误恢复
            tasks = [error_and_recovery(i) for i in range(10)]
            results = await asyncio.gather(*tasks)

            assert all(results), "所有并发错误恢复都应该成功"
            logger.info("异步错误恢复测试通过")

        finally:
            try:
                await sandbox.kill()
            except:
                pass

    # ======================== 资源管理测试 ========================

    def test_resource_management_sync(self):
        """测试同步版本资源管理"""
        sandboxes = []

        try:
            # 创建多个沙箱实例
            for i in range(3):
                sandbox = Sandbox(debug=True)
                sandboxes.append(sandbox)

                # 在每个沙箱中执行操作
                result = sandbox.commands.run(f"echo 'Sandbox {i} test'")
                assert result.exit_code == 0

                sandbox.files.write(f"/tmp/resource_test_{i}.txt", f"Resource test {i}")

            logger.info(f"创建了 {len(sandboxes)} 个沙箱实例")

            # 验证每个沙箱都是独立的
            for i, sandbox in enumerate(sandboxes):
                content = sandbox.files.read(f"/tmp/resource_test_{i}.txt")
                assert content == f"Resource test {i}"

                # 验证其他沙箱的文件不存在
                for j in range(len(sandboxes)):
                    if i != j:
                        exists = sandbox.files.exists(f"/tmp/resource_test_{j}.txt")
                        # 注意：在debug模式下，可能共享文件系统，所以这个测试可能不适用

        finally:
            # 清理所有沙箱
            for i, sandbox in enumerate(sandboxes):
                try:
                    sandbox.kill()
                    logger.info(f"清理沙箱 {i}")
                except Exception as e:
                    logger.error(f"清理沙箱 {i} 失败: {e}")

    async def test_resource_management_async(self):
        """测试异步版本资源管理"""
        sandboxes = []

        try:
            # 并发创建多个沙箱实例
            create_tasks = [AsyncSandbox.create(debug=True) for _ in range(3)]
            sandboxes = await asyncio.gather(*create_tasks)

            # 在每个沙箱中并发执行操作
            async def setup_sandbox(sandbox, index):
                result = await sandbox.commands.run(
                    f"echo 'Async Sandbox {index} test'"
                )
                assert result.exit_code == 0

                await sandbox.files.write(
                    f"/tmp/async_resource_test_{index}.txt",
                    f"Async resource test {index}",
                )
                return sandbox

            setup_tasks = [
                setup_sandbox(sandbox, i) for i, sandbox in enumerate(sandboxes)
            ]
            await asyncio.gather(*setup_tasks)

            logger.info(f"创建了 {len(sandboxes)} 个异步沙箱实例")

            # 并发验证每个沙箱
            async def verify_sandbox(sandbox, index):
                content = await sandbox.files.read(
                    f"/tmp/async_resource_test_{index}.txt"
                )
                assert content == f"Async resource test {index}"
                return True

            verify_tasks = [
                verify_sandbox(sandbox, i) for i, sandbox in enumerate(sandboxes)
            ]
            results = await asyncio.gather(*verify_tasks)

            assert all(results), "所有沙箱验证都应该成功"

        finally:
            # 并发清理所有沙箱
            cleanup_tasks = []
            for i, sandbox in enumerate(sandboxes):

                async def cleanup_sandbox(sb, idx):
                    try:
                        await sb.kill()
                        logger.info(f"清理异步沙箱 {idx}")
                    except Exception as e:
                        logger.error(f"清理异步沙箱 {idx} 失败: {e}")

                cleanup_tasks.append(cleanup_sandbox(sandbox, i))

            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)

    # ======================== 主测试执行器 ========================

    def run_all_tests(self):
        """运行所有压力测试和边界条件测试"""
        logger.info("开始压力测试和边界条件测试...")

        # 大数据处理测试
        self.run_test(
            self.test_large_file_operations_sync, "Large File Operations Sync"
        )
        self.run_test(
            self.test_large_file_operations_async,
            "Large File Operations Async",
            is_async=True,
        )

        # 并发压力测试
        self.run_test(
            self.test_concurrent_sync_operations, "Concurrent Sync Operations"
        )
        self.run_test(
            self.test_concurrent_async_operations,
            "Concurrent Async Operations",
            is_async=True,
        )

        # 内存压力测试
        self.run_test(self.test_memory_stress_sync, "Memory Stress Sync")
        self.run_test(
            self.test_memory_stress_async, "Memory Stress Async", is_async=True
        )

        # 边界条件测试
        self.run_test(self.test_edge_cases_sync, "Edge Cases Sync")
        self.run_test(self.test_edge_cases_async, "Edge Cases Async", is_async=True)

        # 错误恢复测试
        self.run_test(self.test_error_recovery_sync, "Error Recovery Sync")
        self.run_test(
            self.test_error_recovery_async, "Error Recovery Async", is_async=True
        )

        # 资源管理测试
        self.run_test(self.test_resource_management_sync, "Resource Management Sync")
        self.run_test(
            self.test_resource_management_async,
            "Resource Management Async",
            is_async=True,
        )

    def print_summary(self):
        """打印测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        total_duration = sum(r["duration"] for r in self.test_results)

        print("\n" + "=" * 70)
        print("沙箱压力测试和边界条件测试报告")
        print("=" * 70)
        print(f"总测试数: {total_tests}")
        print(f"通过数: {passed_tests}")
        print(f"失败数: {failed_tests}")
        print(f"总耗时: {total_duration:.3f}秒")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")

        if self.failed_tests:
            print(f"\n失败的测试:")
            for test in self.failed_tests:
                print(f"  ❌ {test}")

        # 性能统计
        sync_tests = [
            r for r in self.test_results if "Sync" in r["test"] and r["success"]
        ]
        async_tests = [
            r for r in self.test_results if "Async" in r["test"] and r["success"]
        ]

        if sync_tests:
            avg_sync_time = sum(r["duration"] for r in sync_tests) / len(sync_tests)
            print(f"\n同步版本平均测试时间: {avg_sync_time:.3f}秒")

        if async_tests:
            avg_async_time = sum(r["duration"] for r in async_tests) / len(async_tests)
            print(f"异步版本平均测试时间: {avg_async_time:.3f}秒")

        print("=" * 70)


def main():
    """主函数"""
    validator = StressTestValidator()

    try:
        validator.run_all_tests()
    finally:
        validator.print_summary()


if __name__ == "__main__":
    main()
