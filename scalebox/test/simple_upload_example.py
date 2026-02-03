#!/usr/bin/env python3
"""
简单的 100MB 文件上传示例
使用 sandbox_sync.filesystem.filesystem.py 上传文件到沙箱
"""

import os
import time
import logging
from scalebox.sandbox_sync.main import Sandbox
from scalebox.connection_config import ConnectionConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_test_file(file_path: str, size_mb: int = 100):
    """创建指定大小的测试文件"""
    logger.info(f"创建 {size_mb}MB 测试文件: {file_path}")

    file_size = size_mb * 1024 * 1024  # 转换为字节
    chunk_size = 1024 * 1024  # 1MB 块

    with open(file_path, "wb") as f:
        written = 0
        while written < file_size:
            # 生成测试数据
            chunk_data = bytes(
                [i % 256 for i in range(min(chunk_size, file_size - written))]
            )
            f.write(chunk_data)
            written += len(chunk_data)

            if written % (10 * 1024 * 1024) == 0:  # 每10MB显示进度
                logger.info(f"进度: {written // (1024*1024)}MB")

    logger.info(f"文件创建完成: {os.path.getsize(file_path) / (1024*1024):.2f}MB")


def main():
    """主函数 - 演示文件上传"""

    # 1. 创建 100MB 测试文件
    test_file = "/tmp/test_100mb.bin"
    create_test_file(test_file, 100)

    # 2. 创建沙箱连接配置
    connection_config = ConnectionConfig(
        debug=True, request_timeout=300.0  # 调试模式  # 5分钟超时
    )

    # 3. 创建沙箱实例
    logger.info("连接沙箱...")
    sandbox = Sandbox(
        sandbox_id="upload_test_sandbox",
        sandbox_domain=None,
        envd_version="v1.0",
        envd_access_token=None,
        connection_config=connection_config,
    )

    try:
        # 4. 检查沙箱状态
        if not sandbox.is_running():
            logger.error("沙箱未运行")
            return

        logger.info(f"沙箱连接成功: {sandbox.sandbox_id}")

        # 5. 读取本地文件
        logger.info("读取本地文件...")
        start_time = time.time()

        with open(test_file, "rb") as f:
            file_data = f.read()

        read_time = time.time() - start_time
        logger.info(
            f"文件读取完成: {len(file_data) / (1024*1024):.2f}MB, 耗时: {read_time:.2f}秒"
        )

        # 6. 上传文件到沙箱
        logger.info("开始上传文件到沙箱...")
        upload_start = time.time()

        # 使用 filesystem.write 方法上传
        result = sandbox.files.write("/tmp/uploaded_100mb.bin", file_data)

        upload_time = time.time() - upload_start
        logger.info(f"上传完成: {result.path}")
        logger.info(f"上传耗时: {upload_time:.2f}秒")
        logger.info(f"上传速度: {len(file_data) / (1024*1024) / upload_time:.2f} MB/s")

        # 7. 验证上传结果
        logger.info("验证上传结果...")

        # 检查文件是否存在
        if sandbox.files.exists("/tmp/uploaded_100mb.bin"):
            logger.info("✅ 文件上传成功")

            # 获取文件信息
            file_info = sandbox.files.get_info("/tmp/uploaded_100mb.bin")
            logger.info(f"文件信息: 路径={file_info.path}, 大小={file_info.size}字节")

        else:
            logger.error("❌ 文件上传失败")

    except Exception as e:
        logger.error(f"上传过程中发生错误: {e}")

    finally:
        # 8. 清理资源
        try:
            sandbox.kill()
            logger.info("沙箱已清理")
        except Exception as e:
            logger.warning(f"清理沙箱时发生错误: {e}")

        # 删除本地测试文件
        try:
            os.remove(test_file)
            logger.info("本地测试文件已删除")
        except Exception as e:
            logger.warning(f"删除本地文件时发生错误: {e}")


if __name__ == "__main__":
    main()
