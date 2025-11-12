#!/usr/bin/env python3
"""
Test cases for connect and pause functionality (synchronous version).

This test suite validates:
- Creating a sandbox
- Adding and deleting files before pause
- Pausing the sandbox
- Connecting to the paused sandbox
- Verifying file operations after connect
"""

import time

from scalebox.sandbox.filesystem.filesystem import WriteInfo, FileType
from scalebox.sandbox_sync.main import Sandbox


class ConnectPauseSyncTest:
    """Test suite for connect and pause functionality (sync)."""

    def __init__(self):
        self.sandbox = None
        self.sandbox_id = None
        self.test_results = []

    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")

    def test_connect_pause_with_files(self):
        """测试connect和pause功能，包含文件操作"""
        try:
            # 1. 创建沙箱
            print("Step 1: Creating sandbox...")
            self.sandbox = Sandbox.create(
                template="code-interpreter",
                timeout=3600,
                metadata={"test": "connect_pause_sync"},
                envs={"TEST_ENV": "sync_test"},
            )
            self.sandbox_id = self.sandbox.sandbox_id
            assert self.sandbox is not None
            assert self.sandbox_id is not None
            print(f"Created sandbox with ID: {self.sandbox_id}")

            # 2. 在pause之前增加文件
            print("Step 2: Adding files before pause...")
            test_files = {
                "/tmp/test_file1.txt": "Content of test file 1",
                "/tmp/test_file2.txt": "Content of test file 2",
                "/tmp/test_file3.bin": b"Binary content for test file 3",
            }

            for file_path, content in test_files.items():
                result = self.sandbox.files.write(file_path, content)
                print(result)
                assert isinstance(result, WriteInfo)
                assert self.sandbox.files.exists(file_path)
                print(f"Created file: {file_path}")

            # 3. 在pause之前删除一个文件
            print("Step 3: Deleting a file before pause...")
            file_to_delete = "/tmp/test_file2.txt"
            self.sandbox.files.remove(file_to_delete)
            assert not self.sandbox.files.exists(file_to_delete)
            print(f"Deleted file: {file_to_delete}")

            # 4. 创建目录和文件
            print("Step 4: Creating directory and nested files...")
            self.sandbox.files.make_dir("/tmp/test_dir")
            self.sandbox.files.write("/tmp/test_dir/nested_file.txt", "Nested file content")
            assert self.sandbox.files.exists("/tmp/test_dir")
            assert self.sandbox.files.exists("/tmp/test_dir/nested_file.txt")
            print("Created directory and nested file")

            # 5. Pause沙箱
            print("Step 5: Pausing sandbox...")
            self.sandbox.beta_pause()
            print("Sandbox paused successfully")

            # 等待一小段时间确保pause完成
            time.sleep(1)

            # 6. Connect到暂停的沙箱
            print("Step 6: Connecting to paused sandbox...")
            connected_sandbox = Sandbox.connect(self.sandbox_id)
            print(connected_sandbox)
            assert connected_sandbox.sandbox_id == self.sandbox_id
            print("Connected to sandbox successfully")

            # 等待一小段时间确保connect完成
            time.sleep(2)

            # 7. 在connect之后校验文件操作结果
            print("Step 7: Verifying file operations after connect...")

            # 校验应该存在的文件
            assert connected_sandbox.files.exists("/tmp/test_file1.txt"), "test_file1.txt should exist"
            file1_content = connected_sandbox.files.read("/tmp/test_file1.txt", format="text")
            assert "Content of test file 1" in file1_content
            print("✅ Verified test_file1.txt exists and content is correct")

            assert connected_sandbox.files.exists("/tmp/test_file3.bin"), "test_file3.bin should exist"
            file3_content = connected_sandbox.files.read("/tmp/test_file3.bin", format="bytes")
            assert bytes(file3_content) == b"Binary content for test file 3"
            print("✅ Verified test_file3.bin exists and content is correct")

            # 校验应该不存在的文件（被删除的）
            assert not connected_sandbox.files.exists("/tmp/test_file2.txt"), "test_file2.txt should not exist"
            print("✅ Verified test_file2.txt was deleted correctly")

            # 校验目录和嵌套文件
            assert connected_sandbox.files.exists("/tmp/test_dir"), "test_dir should exist"
            assert connected_sandbox.files.exists("/tmp/test_dir/nested_file.txt"), "nested_file.txt should exist"
            nested_content = connected_sandbox.files.read("/tmp/test_dir/nested_file.txt", format="text")
            assert "Nested file content" in nested_content
            print("✅ Verified directory and nested file exist and content is correct")

            # 8. 在connect后的沙箱中执行一些操作验证功能正常
            print("Step 8: Verifying sandbox functionality after connect...")
            result = connected_sandbox.commands.run("echo 'Test command after connect'")
            assert result.exit_code == 0
            assert "Test command after connect" in result.stdout
            print("✅ Verified sandbox commands work after connect")

            # 9. 创建新文件验证写入功能正常
            print("Step 9: Testing file write after connect...")
            new_file_path = "/tmp/new_file_after_connect.txt"
            connected_sandbox.files.write(new_file_path, "New file created after connect")
            assert connected_sandbox.files.exists(new_file_path)
            new_content = connected_sandbox.files.read(new_file_path, format="text")
            assert "New file created after connect" in new_content
            print("✅ Verified file write works after connect")

            self.log_test_result("Connect and Pause with Files", True, "All verifications passed")
            return True

        except Exception as e:
            self.log_test_result("Connect and Pause with Files", False, str(e))
            print(f"Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_connect_pause_multiple_operations(self):
        """测试多次pause和connect操作"""
        try:
            # 1. 创建沙箱
            print("Test 2: Creating sandbox for multiple operations test...")
            sandbox = Sandbox.create(
                template="base",
                timeout=3600,
                metadata={"test": "connect_pause_multiple_sync"},
            )
            sandbox_id = sandbox.sandbox_id
            print(f"Created sandbox with ID: {sandbox_id}")

            # 2. 第一次操作：创建文件
            print("First operation: Creating files...")
            sandbox.files.write("/tmp/multi_test1.txt", "First batch")
            sandbox.files.write("/tmp/multi_test2.txt", "First batch")

            # 3. 第一次pause
            print("First pause...")
            sandbox.beta_pause()
            time.sleep(2)

            # 4. 第一次connect
            print("First connect...")
            sandbox = Sandbox.connect(sandbox_id)
            time.sleep(2)

            # 5. 验证第一次的文件存在
            assert sandbox.files.exists("/tmp/multi_test1.txt")
            assert sandbox.files.exists("/tmp/multi_test2.txt")

            # 6. 第二次操作：删除一个文件，创建新文件
            print("Second operation: Deleting and creating files...")
            sandbox.files.remove("/tmp/multi_test1.txt")
            sandbox.files.write("/tmp/multi_test3.txt", "Second batch")

            # 7. 第二次pause
            print("Second pause...")
            sandbox.beta_pause()
            time.sleep(2)

            # 8. 第二次connect
            print("Second connect...")
            sandbox = Sandbox.connect(sandbox_id)
            time.sleep(2)

            # 9. 验证第二次操作的结果
            assert not sandbox.files.exists("/tmp/multi_test1.txt"), "multi_test1.txt should be deleted"
            assert sandbox.files.exists("/tmp/multi_test2.txt"), "multi_test2.txt should exist"
            assert sandbox.files.exists("/tmp/multi_test3.txt"), "multi_test3.txt should exist"
            content = sandbox.files.read("/tmp/multi_test3.txt", format="text")
            assert "Second batch" in content

            # 清理
            sandbox.kill()

            self.log_test_result("Multiple Connect and Pause Operations", True, "All verifications passed")
            return True

        except Exception as e:
            self.log_test_result("Multiple Connect and Pause Operations", False, str(e))
            print(f"Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup(self):
        """清理资源"""
        if self.sandbox:
            try:
                self.sandbox.kill()
                print("Sandbox cleaned up successfully")
            except Exception as e:
                print(f"Error cleaning up sandbox: {e}")

    def print_summary(self):
        """打印测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        print("\n" + "=" * 60)
        print("Connect and Pause Test Report (Sync)")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过数: {passed_tests}")
        print(f"失败数: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")

        if failed_tests > 0:
            print(f"\n失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['message']}")

        print("=" * 60)


def main():
    """主函数"""
    test_suite = ConnectPauseSyncTest()

    try:
        # 运行测试
        test_suite.test_connect_pause_with_files()
        # test_suite.test_connect_pause_multiple_operations()
    finally:
        test_suite.cleanup()
        test_suite.print_summary()


if __name__ == "__main__":
    main()

