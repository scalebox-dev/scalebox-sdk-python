#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""
示例：如何在创建异步 Sandbox 时携带 object_storage 参数。

运行前准备：
1. 设置环境变量 SCALEBOX_OBJECT_STORAGE_CONFIG 为 JSON 字符串或 JSON 文件路径，
   该内容会被原样传递给后端。例如：
   {
       "provider": "s3",
       "bucket": "my-sbx-bucket",
       "region": "us-east-1",
       "access_key_id": "AKIA...",
       "secret_access_key": "******",
       "endpoint": "https://s3.amazonaws.com"
   }
2. （可选）设置 SCALEBOX_OBJECT_STORAGE_TEMPLATE / SCALEBOX_OBJECT_STORAGE_TIMEOUT
   调整模板和沙箱超时时间。

注意：object_storage 功能仍主要在同步版本可用，异步示例取决于后端实际支持状况。
      需要在提供有效配置后手动执行：

      PYTHONPATH=/home/ubuntu/git_home/scalebox:$PYTHONPATH \\
      SCALEBOX_OBJECT_STORAGE_CONFIG=/path/to/config.json \\
      python test/test_sandbox_object_storage_example_async.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from scalebox.exceptions import SandboxException
from scalebox.sandbox_async.main import AsyncSandbox
from scalebox.sandbox.sandbox_api import SandboxQuery

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# CONFIG_ENV = "SCALEBOX_OBJECT_STORAGE_CONFIG"
# TEMPLATE_ENV = "SCALEBOX_OBJECT_STORAGE_TEMPLATE"
# TIMEOUT_ENV = "SCALEBOX_OBJECT_STORAGE_TIMEOUT"
#
#
# def _load_object_storage_payload() -> Optional[Dict[str, Any]]:
#     raw_value = os.environ.get(CONFIG_ENV)
#     if not raw_value:
#         logger.warning(
#             "未检测到 %s 环境变量，跳过 object_storage 示例。请设置 JSON 配置后重新运行。",
#             CONFIG_ENV,
#         )
#         return None
#
#     config_text: Optional[str] = None
#     potential_path = Path(raw_value)
#     if potential_path.is_file():
#         config_text = potential_path.read_text(encoding="utf-8")
#     else:
#         config_text = raw_value
#
#     try:
#         payload = json.loads(config_text)
#     except json.JSONDecodeError as exc:
#         logger.error("无法解析 object_storage 配置（需合法 JSON）：%s", exc)
#         raise SystemExit(1) from exc
#
#     if not isinstance(payload, dict):
#         logger.error("object_storage 配置必须是 JSON 对象，示例详见文件头部注释。")
#         raise SystemExit(1)
#
#     return payload
#
#
# def _mask_value(value: str) -> str:
#     if len(value) <= 4:
#         return "*" * len(value)
#     return f"{value[:2]}***{value[-2:]}"
#
#
# def _display_object_storage_keys(config: Dict[str, Any]) -> Dict[str, Any]:
#     masked = {}
#     for key, value in config.items():
#         if isinstance(value, str):
#             masked[key] = _mask_value(value)
#         else:
#             masked[key] = value
#     return masked


async def create_sandbox_with_object_storage_async():
    # payload = _load_object_storage_payload()
    # if payload is None:
    #     return
    #
    # template = os.environ.get(TEMPLATE_ENV, "base")
    # timeout = int(os.environ.get(TIMEOUT_ENV, "600"))

    sandbox: Optional[AsyncSandbox] = None
    try:
        sandbox = await AsyncSandbox.create(
            template="base",
            timeout=3600,
            metadata={"example": "object_storage_async"},
            object_storage={
                "uri": "s3://bgd-test/test/",
                "mount_point": "/mnt/oss",
                "access_key": "",
                "secret_key": "",
                "region": "us-east-2",
                "endpoint": "https://s3.us-east-2.amazonaws.com",
            },
        )
        print(sandbox.sandbox_id)
        print(sandbox.sandbox_domain)
        if sandbox.object_storage:
            print(sandbox.object_storage)

        info = await sandbox.get_info()
        print(info)
        print(f"get_info.object_storage: {info.object_storage}")

        listed = await AsyncSandbox.list(
            query=SandboxQuery(metadata={"example": "object_storage_async"})
        )
        print(f"Async list 根据 metadata 命中的沙箱数量: {len(listed)}")
        for listed_box in listed:
            detailed = await AsyncSandbox.get_info(sandbox_id=listed_box.sandbox_id)
            print(detailed)
            print(
                f"list -> sandbox {listed_box.sandbox_id} object_storage: {detailed.object_storage}"
            )

        # 在沙箱中运行简单命令，确认可正常访问
        result = await sandbox.commands.run("echo 'async object storage sandbox is ready'")
        print(f"命令输出: {result.stdout.strip()}")
    except SandboxException as exc:
        logger.error("创建或使用异步沙箱失败：%s", exc)
        raise
    finally:
        if sandbox is not None:
            # await sandbox.kill()
            logger.info("异步沙箱已销毁")


if __name__ == "__main__":
    asyncio.run(create_sandbox_with_object_storage_async())

