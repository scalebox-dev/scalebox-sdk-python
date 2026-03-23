#!/usr/bin/env python3
"""
Sidecar s3fs_gateway basic test.

流程：
1. 使用 AsyncSandbox / Sandbox 创建一个 sandbox（template=nginx/base）。
2. 调用封装好的 `mount_s3fs_gateway` 方法，在 sandbox 内执行 s3fs_gateway 命令。
3. 校验命令是否执行成功（exit_code == 0），必要时打印 stdout/stderr。

说明：
- 该测试假设 sandbox 模板里已经集成 sandboxagent sidecar，并且 sidecar 支持 s3fs_gateway 命令。
- S3 凭证可以通过参数 --ak/--sk 传入，或通过环境变量传入，依赖后端实现。
- 为避免在没有有效凭证的环境下误报失败，若未配置必要的环境变量，测试会直接跳过。
"""

import asyncio
import logging
import os
from typing import Optional, Tuple

from scalebox.exceptions import SandboxException
from scalebox.sandbox_async.main import AsyncSandbox
from scalebox.sandbox_sync.main import Sandbox

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _get_env_required(name: str) -> Optional[str]:
    value = os.getenv(name)
    if not value:
        logger.warning("Env %s is not set; s3fs_gateway test may be skipped", name)
    return value


def _get_s3fs_config() -> Optional[Tuple[str, str, str, str, str]]:
    """
    统一从环境变量读取 s3fs_gateway 所需的配置。

    返回: (uri, endpoint, region, ak, sk) 或 None（表示跳过测试）
    """
    uri = os.getenv("S3FS_TEST_URI", "s3://scalex-packages/test/")
    endpoint = os.getenv("S3FS_TEST_ENDPOINT", "https://s3.us-east-2.amazonaws.com")
    region = os.getenv("S3FS_TEST_REGION", "us-east-2")

    ak = _get_env_required("S3FS_ACCESS_KEY")
    sk = _get_env_required("S3FS_SECRET_KEY")
    if not ak or not sk:
        logger.warning(
            "S3FS_ACCESS_KEY / S3FS_SECRET_KEY not set, skip s3fs_gateway_sidecar test."
        )
        return None
    return uri, endpoint, region, ak, sk


async def run_s3fs_gateway_test() -> None:
    cfg = _get_s3fs_config()
    if cfg is None:
        return
    uri, endpoint, region, ak, sk = cfg

    logger.info("Creating sandbox for s3fs_gateway test...")
    sandbox: AsyncSandbox = await AsyncSandbox.create(
        template="nginx",
        timeout=3600,
        metadata={"test": "s3fs_gateway_sidecar"},
        envs={},  # 如需特殊环境可在此处补充
    )

    try:
        logger.info("Created sandbox: %s", sandbox.sandbox_id)

        logger.info("Running s3fs_gateway via AsyncSandbox.mount_s3fs_gateway...")
        result, mount_point = await sandbox.mount_s3fs_gateway(
            uri=uri,
            ak=ak,
            sk=sk,
            region=region,
            endpoint=endpoint,
            extra_options=["-o", "rw"],
        )

        logger.info(
            "Command finished: exit_code=%s, stdout_len=%d, stderr_len=%d",
            result.exit_code,
            len(result.stdout or ""),
            len(result.stderr or ""),
        )

        if result.exit_code != 0:
            logger.error("s3fs_gateway command failed")
            logger.error("stdout:\n%s", result.stdout)
            logger.error("stderr:\n%s", result.stderr)
            raise SandboxException(
                f"s3fs_gateway failed with exit_code={result.exit_code}",
                details={"stdout": result.stdout, "stderr": result.stderr},
            )

        # 可选：简单验证挂载点是否存在（不强制要求）
        try:
            check_cmd = f"mount | grep ' {mount_point} ' || (echo 'not mounted' && exit 1)"
            check_res = await sandbox.commands.run(check_cmd)
            if check_res.exit_code != 0:
                logger.warning(
                    "Mount verification failed (exit=%s). stdout:\n%s\nstderr:\n%s",
                    check_res.exit_code,
                    check_res.stdout,
                    check_res.stderr,
                )
            else:
                logger.info("Mount point %s verified in sandbox.", mount_point)
        except Exception as e:  # noqa: BLE001
            logger.warning("Mount verification raised exception: %s", e)

    finally:
        # 尽量清理 sandbox，避免泄露资源
        try:
            await sandbox.kill()
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to kill sandbox %s: %s", sandbox.sandbox_id, e)


def run_s3fs_gateway_test_sync() -> None:
    cfg = _get_s3fs_config()
    if cfg is None:
        return
    uri, endpoint, region, ak, sk = cfg

    logger.info("Creating sync sandbox for s3fs_gateway test...")
    sandbox = Sandbox.create(
        template="nginx",
        timeout=3600,
        metadata={"test": "s3fs_gateway_sidecar_sync"},
        envs={},
    )

    try:
        logger.info("Created sync sandbox: %s", sandbox.sandbox_id)

        logger.info("Running s3fs_gateway via Sandbox.mount_s3fs_gateway...")
        result, mount_point = sandbox.mount_s3fs_gateway(
            uri=uri,
            ak=ak,
            sk=sk,
            region=region,
            endpoint=endpoint,
            extra_options=["-o", "rw"],
        )
        logger.info(
            "Sync command finished: exit_code=%s, stdout_len=%d, stderr_len=%d",
            result.exit_code,
            len(result.stdout or ""),
            len(result.stderr or ""),
        )
        if result.exit_code != 0:
            logger.error("sync s3fs_gateway command failed")
            logger.error("stdout:\n%s", result.stdout)
            logger.error("stderr:\n%s", result.stderr)
            raise SandboxException(
                f"sync s3fs_gateway failed with exit_code={result.exit_code}",
                details={"stdout": result.stdout, "stderr": result.stderr},
            )

        # 可选：简单验证挂载点是否存在（不强制要求）
        try:
            check_cmd = f"mount | grep ' {mount_point} ' || (echo 'not mounted' && exit 1)"
            check_res = sandbox.commands.run(check_cmd)
            if check_res.exit_code != 0:
                logger.warning(
                    "Sync mount verification failed (exit=%s). stdout:\n%s\nstderr:\n%s",
                    check_res.exit_code,
                    check_res.stdout,
                    check_res.stderr,
                )
            else:
                logger.info("Sync mount point %s verified in sandbox.", mount_point)
        except Exception as e:  # noqa: BLE001
            logger.warning("Sync mount verification raised exception: %s", e)

    finally:
        try:
            sandbox.kill()
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to kill sync sandbox %s: %s", sandbox.sandbox_id, e)


def main() -> None:
    # 先跑 sync，再跑 async 版本，两个都调用各自的 mount_s3fs_gateway 封装方法
    run_s3fs_gateway_test_sync()
    asyncio.run(run_s3fs_gateway_test())


if __name__ == "__main__":
    main()

