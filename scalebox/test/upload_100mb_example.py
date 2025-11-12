#!/usr/bin/env python3
"""
使用 sandbox_sync.filesystem.filesystem.py 上传 100MB 本地文件的示例

这个示例演示了如何：
1. 创建一个 100MB 的本地测试文件
2. 连接到沙箱
3. 使用 Filesystem 类上传文件到沙箱
4. 验证上传结果
"""

import os
import time
import logging
from io import BytesIO
from scalebox.sandbox_sync.main import Sandbox
from scalebox.connection_config import ConnectionConfig

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_100mb_test_file(file_path: str = "/home/test_100mb.bin") -> str:
    """
    创建一个 100MB 的测试文件
    
    Args:
        file_path: 本地文件路径
        
    Returns:
        创建的文件路径
    """
    logger.info(f"开始创建 100MB 测试文件: {file_path}")
    start_time = time.time()
    
    # 创建 100MB 的数据 (100 * 1024 * 1024 字节)
    file_size = 1000 * 1024 * 1024  # 100MB
    chunk_size = 1024 * 1024  # 1MB 块大小
    
    with open(file_path, 'wb') as f:
        written = 0
        while written < file_size:
            # 生成 1MB 的数据块，包含一些模式以便验证
            chunk_data = bytes([(i + written) % 256 for i in range(chunk_size)])
            f.write(chunk_data)
            written += chunk_size
            
            # 显示进度
            if written % (10 * 1024 * 1024) == 0:  # 每 10MB 显示一次
                progress = (written / file_size) * 100
                logger.info(f"创建进度: {progress:.1f}% ({written // (1024*1024)}MB)")
    
    creation_time = time.time() - start_time
    actual_size = os.path.getsize(file_path)
    logger.info(f"文件创建完成: {actual_size / (1024*1024):.2f}MB, 耗时: {creation_time:.2f}秒")
    
    return file_path

def upload_file_to_sandbox(local_file_path: str, sandbox_path: str = "/tmp/uploaded_100mb.bin"):
    """
    将本地文件上传到沙箱
    
    Args:
        local_file_path: 本地文件路径
        sandbox_path: 沙箱中的目标路径
    """
    logger.info("开始连接沙箱...")
    
    # 创建沙箱连接配置
    sandbox = Sandbox.create(
        timeout=3600,
        # debug=True,
        metadata={"test": "code_interpreter_validation"},
        envs={"CI_TEST": "sync_test"},
    )

    try:
        # 检查沙箱是否运行
        if not sandbox.is_running():
            logger.error("沙箱未运行，无法上传文件")
            return False
            
        logger.info(f"沙箱连接成功，ID: {sandbox.sandbox_id}")
        
        # 读取本地文件
        logger.info(f"读取本地文件: {local_file_path}")
        start_time = time.time()
        
        with open(local_file_path, 'rb') as f:
            file_data = f.read()
            
        read_time = time.time() - start_time
        logger.info(f"文件读取完成: {len(file_data) / (1024*1024):.2f}MB, 耗时: {read_time:.2f}秒")
        
        # 上传文件到沙箱
        logger.info(f"开始上传文件到沙箱: {sandbox_path}")
        upload_start = time.time()
        
        # 使用 filesystem.write 方法上传文件
        result = sandbox.files.write(sandbox_path, file_data,"root",3600)
        
        upload_time = time.time() - upload_start
        logger.info(f"文件上传完成: {result.path}, 耗时: {upload_time:.2f}秒")
        logger.info(f"上传速度: {len(file_data) / (1024*1024) / upload_time:.2f} MB/s")
        
        # 验证上传结果
        logger.info("验证上传结果...")
        verify_start = time.time()
        
        # 检查文件是否存在
        if sandbox.files.exists(sandbox_path):
            logger.info("✅ 文件在沙箱中存在")
            
            # 获取文件信息
            file_info = sandbox.files.get_info(sandbox_path)
            logger.info(f"文件信息: {file_info}")
            
            # 读取文件内容进行验证（只读取前1MB进行快速验证）
            logger.info("验证文件内容...")
            with open(local_file_path, 'rb') as f:
                local_sample = f.read(1024 * 1024)  # 读取前1MB
            
            sandbox_sample = sandbox.files.read(sandbox_path, format="bytes")[:1024 * 1024]
            
            if local_sample == sandbox_sample:
                logger.info("✅ 文件内容验证成功")
            else:
                logger.error("❌ 文件内容验证失败")
                return False
                
        else:
            logger.error("❌ 文件在沙箱中不存在")
            return False
            
        verify_time = time.time() - verify_start
        total_time = time.time() - upload_start
        logger.info(f"验证完成，耗时: {verify_time:.2f}秒")
        logger.info(f"总上传时间: {total_time:.2f}秒")
        
        return True
        
    except Exception as e:
        logger.error(f"上传过程中发生错误: {e}")
        return False
        
    finally:
        # 清理沙箱
        try:
            sandbox.kill()
            logger.info("沙箱已清理")
        except Exception as e:
            logger.warning(f"清理沙箱时发生错误: {e}")

def upload_file_streaming(local_file_path: str, sandbox_path: str = "/tmp/uploaded_100mb_streaming.bin"):
    """
    使用真正的流式方式上传文件（不将整个文件读入内存）。

    通过沙箱已配置的 HTTP 客户端发起 multipart/form-data 请求，直接传入文件对象，
    由 HTTPX 以流的方式读取并上传内容。

    Args:
        local_file_path: 本地文件路径
        sandbox_path: 沙箱中的目标路径
    """
    logger.info("开始流式上传文件...")

    sandbox = Sandbox.create(
        timeout=3600,
        # debug=True,
        metadata={"test": "code_interpreter_validation"},
        envs={"CI_TEST": "sync_test"},
    )

    try:
        if not sandbox.is_running():
            logger.error("沙箱未运行，无法上传文件")
            return False

        logger.info(f"沙箱连接成功，ID: {sandbox.sandbox_id}")

        file_size = os.path.getsize(local_file_path)
        logger.info(f"文件大小: {file_size / (1024*1024):.2f}MB")

        start_time = time.time()

        with open(local_file_path, "rb") as f:
            sandbox.files.write(sandbox_path, f,"root",3600)

        upload_time = time.time() - start_time
        logger.info(f"流式上传完成，总耗时: {upload_time:.2f}秒")
        logger.info(f"平均速度: {file_size / (1024*1024) / upload_time:.2f} MB/s")

        # 验证文件是否存在
        if sandbox.files.exists(sandbox_path):
            info = sandbox.files.get_info(sandbox_path)
            logger.info(f"✅ 文件已存在于沙箱: 路径={info.path}, 大小={info.size} 字节")
            return True

        logger.error("❌ 文件在沙箱中不存在")
        return False

    except Exception as e:
        logger.error(f"流式上传过程中发生错误: {e}")
        return False

    finally:
        try:
            sandbox.kill()
            logger.info("沙箱已清理")
        except Exception as e:
            logger.warning(f"清理沙箱时发生错误: {e}")

def upload_file_chunked_32m(local_file_path: str, sandbox_path: str = "/tmp/uploaded_100mb_chunked_32m.bin"):
    """
    使用客户端 32MB 分片方式上传：
    - 本地读取 32MB 分片，逐片上传为临时文件 {sandbox_path}.partXXXXXX
    - 在沙箱内通过 `cat` 合并为最终文件
    - 合并成功后删除临时分片

    Args:
        local_file_path: 本地文件路径
        sandbox_path: 沙箱中的目标路径（合并后的最终文件路径）
    """
    logger.info("开始 32MB 分片上传...")

    sandbox = Sandbox.create(
        template="code-interpreter",
        timeout=3600,
        # debug=True,
        metadata={"test": "code_interpreter_validation"},
        envs={"CI_TEST": "sync_test"},
    )

    try:
        if not sandbox.is_running():
            logger.error("沙箱未运行，无法上传文件")
            return False

        file_size = os.path.getsize(local_file_path)
        logger.info(f"文件大小: {file_size / (1024*1024):.2f}MB")

        chunk_size = 8 * 1024 * 1024  # 32MB 客户端缓存/分片大小
        start_time = time.time()

        part_index = 0
        uploaded_parts = []

        with open(local_file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                part_name = f"{sandbox_path}.part{part_index:06d}"
                t0 = time.time()
                sandbox.files.write(part_name, chunk)
                dt = time.time() - t0
                uploaded_parts.append(part_name)
                logger.info(
                    f"已上传分片 #{part_index} -> {part_name} 大小={(len(chunk)/(1024*1024)):.2f}MB, 用时={dt:.2f}s"
                )
                part_index += 1

        if not uploaded_parts:
            logger.error("未读取到任何分片，上传失败")
            return False

        # 在沙箱中合并分片，确保按编号顺序连接
        logger.info("开始在沙箱内合并分片...")
        concat_cmd = (
            f"bash -lc 'cat {' '.join(uploaded_parts)} > {sandbox_path}'"
        )
        proc = sandbox.commands.run(concat_cmd)
        if proc.exit_code != 0:
            logger.error(f"合并失败: exit={proc.exit_code}, stderr=\n{proc.stderr}")
            return False

        # 校验合并后的文件大小
        info = sandbox.files.get_info(sandbox_path)
        if info.size != file_size:
            logger.error(
                f"合并后大小不一致: 期望={file_size}, 实际={info.size}"
            )
            return False

        # 删除分片
        logger.info("删除沙箱内临时分片...")
        rm_cmd = f"bash -lc 'rm -f {sandbox_path}.part*'"
        rm_proc = sandbox.commands.run(rm_cmd)
        if rm_proc.exit_code != 0:
            logger.warning(f"删除分片警告: exit={rm_proc.exit_code}, stderr=\n{rm_proc.stderr}")

        total_time = time.time() - start_time
        logger.info(
            f"✅ 32MB 分片上传完成，总耗时={total_time:.2f}s，平均速度={(file_size/(1024*1024))/total_time:.2f} MB/s"
        )
        return True

    except Exception as e:
        logger.error(f"32MB 分片上传过程中发生错误: {e}")
        return False
    finally:
        try:
            sandbox.kill()
            logger.info("沙箱已清理")
        except Exception as e:
            logger.warning(f"清理沙箱时发生错误: {e}")

def main():
    """主函数"""
    logger.info("=== 100MB 文件上传示例 ===")
    
    # 1. 创建 100MB 测试文件
    local_file = create_100mb_test_file()
    
    try:
        # 2. 方式一：直接上传整个文件
        logger.info("\n=== 方式一：直接上传 ===")
        success1 = upload_file_to_sandbox(local_file, "/tmp/uploaded_100mb_direct.bin")

        if success1:
            logger.info("✅ 直接上传成功")
        else:
            logger.error("❌ 直接上传失败")
        
        # 3. 方式二：流式分块上传
        logger.info("\n=== 方式二：流式上传 ===")
        success2 = upload_file_streaming(local_file, "/home/uploaded_100mb_streaming.bin")
        
        if success2:
            logger.info("✅ 流式上传成功")
        else:
            logger.error("❌ 流式上传失败")
        
        # 4. 方式三：32MB 分片上传（客户端分片 + 服务器端合并）
        logger.info("\n=== 方式三：32MB 分片上传 ===")
        success3 = upload_file_chunked_32m(local_file, "/tmp/uploaded_100mb_chunked_32m.bin")

        if success3:
            logger.info("✅ 32MB 分片上传成功")
        else:
            logger.error("❌ 32MB 分片上传失败")
            
    finally:
        # 4. 清理本地测试文件
        try:
            os.remove(local_file)
            logger.info(f"本地测试文件已删除: {local_file}")
        except Exception as e:
            logger.warning(f"删除本地文件时发生错误: {e}")
    
    logger.info("=== 示例完成 ===")

if __name__ == "__main__":
    main()
