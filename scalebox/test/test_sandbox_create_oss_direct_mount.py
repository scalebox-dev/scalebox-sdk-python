#!/usr/bin/env python3
"""
OSS direct mount：sandbox create 请求体与 NewSandbox 序列化验证（对齐 oss_quick_guide.md）。

结构与 ``test_code_interpreter_async_comprehensive`` 相同：
- ``SandboxOssDirectMountValidator`` 聚合用例
- ``run_test`` / ``log_test_result`` 记录耗时与成败
- ``run_all_tests`` 顺序执行
- ``print_summary`` 输出摘要

前半为 **本地 JSON 形状断言**（无网络）。

设置了 ``SBX_API_KEY`` 时，``test_async_sandbox_create_with_oss_options`` 会按 **多种场景各创建一台沙箱**（与上文 JSON 用例一一对应）；远程沙箱 **不** ``kill``。仅关闭本机 aiohttp/httpx 连接以消除资源告警。未配置 ``S3FS_ACCESS_KEY``/``S3FS_SECRET_KEY`` 时跳过需 OSS 的场景。未设置 ``SBX_API_KEY`` 时整段跳过。

运行::

    PYTHONPATH=<repo-root> python3 scalebox/test/test_sandbox_create_oss_direct_mount.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Tuple

from scalebox.api.client.models.new_sandbox import NewSandbox
from scalebox.exceptions import SandboxException
from scalebox.sandbox_async.main import AsyncSandbox

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _is_retryable_gateway_error(exc: BaseException) -> bool:
    """502/503/504 等网关超时，适合有限次重试。"""
    s = str(exc).lower()
    return any(code in s for code in ("502", "503", "504")) or (
        "gateway" in s and "time" in s
    )


async def _async_sandbox_create_live(
    create_kw: Dict[str, Any],
    *,
    max_attempts: int = 4,
    initial_delay_s: float = 5.0,
) -> Any:
    """
    带重试的 ``AsyncSandbox.create``，缓解 ``direct_mount`` 等慢路径上的 504 Gateway Time-out。

    重试次数可用环境变量 ``OSS_LIVE_CREATE_MAX_ATTEMPTS``（默认 4）覆盖。
    """
    attempts = max(1, int(os.getenv("OSS_LIVE_CREATE_MAX_ATTEMPTS", str(max_attempts))))
    delay = float(os.getenv("OSS_LIVE_CREATE_RETRY_DELAY_S", str(initial_delay_s)))

    last_exc: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await AsyncSandbox.create(**create_kw)
        except SandboxException as e:
            last_exc = e
            if attempt < attempts and _is_retryable_gateway_error(e):
                wait = min(delay * (2 ** (attempt - 1)), 90.0)
                logger.warning(
                    "AsyncSandbox.create attempt %d/%d: %s — retry in %.1fs",
                    attempt,
                    attempts,
                    e,
                    wait,
                )
                await asyncio.sleep(wait)
                continue
            raise
    assert last_exc is not None
    raise last_exc


async def _close_sandbox_local_clients(sandbox: Any) -> None:
    """关闭本机 aiohttp / httpx 连接，不调用 ``kill``，远程沙箱保留。"""
    try:
        await sandbox._session.close()
    except Exception as e:
        logger.debug("aiohttp session close: %s", e)
    try:
        await sandbox._envd_api.aclose()
    except Exception as e:
        logger.debug("httpx envd aclose: %s", e)


def _new_sandbox_minimal(**kwargs: Any) -> NewSandbox:
    return NewSandbox(
        template_id="nginx",
        timeout=600,
        metadata={},
        env_vars={},
        secure=False,
        allow_internet_access=True,
        **kwargs,
    )


class SandboxOssDirectMountValidator:
    """OSS direct mount create body 验证（NewSandbox.to_dict / from_dict）。"""

    def __init__(self) -> None:
        self.test_results: List[Dict[str, Any]] = []
        self.failed_tests: List[str] = []

    async def log_test_result(
        self,
        test_name: str,
        success: bool,
        message: str = "",
        duration: float = 0,
    ) -> None:
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
        logger.info("%s %s (%.3fs) %s", status, test_name, duration, message)

    async def run_test(self, test_func, test_name: str) -> None:
        start_time = time.time()
        try:
            await test_func()
            duration = time.time() - start_time
            await self.log_test_result(test_name, True, duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test_result(test_name, False, str(e), duration=duration)

    # ======================== NewSandbox 序列化（无网络） ========================

    async def test_single_object_storage_dict_with_endpoint(self) -> None:
        """单对象 object_storage + endpoint 空字符串（兼容旧版）。"""
        body = _new_sandbox_minimal(
            object_storage={
                "uri": "s3://scalex-packages/test/",
                "mount_point": "/mnt/oss",
                "access_key": "<AK>",
                "secret_key": "<SK>",
                "region": "us-east-2",
                "endpoint": "",
            },
        )
        d = body.to_dict()
        assert d["template"] == "nginx"
        ospec = d["object_storage"]
        assert isinstance(ospec, dict)
        assert ospec["uri"] == "s3://scalex-packages/test/"
        assert ospec["endpoint"] == ""
        assert ospec["mount_point"] == "/mnt/oss"

    async def test_multi_object_storage_list(self) -> None:
        """多条 object_storage 列表。"""
        mounts: List[Dict[str, Any]] = [
            {
                "uri": "s3://scalex-packages/test/",
                "mount_point": "/mnt/oss",
                "access_key": "<AK>",
                "secret_key": "<SK>",
                "region": "us-east-2",
                "endpoint": "",
            },
            {
                "uri": "s3://scalex-packages/test/ttttt/",
                "mount_point": "/mnt/oss-ttttt",
                "access_key": "<AK>",
                "secret_key": "<SK>",
                "region": "us-east-2",
                "endpoint": "",
            },
        ]
        d = _new_sandbox_minimal(object_storage=mounts).to_dict()
        assert d["object_storage"] == mounts
        assert isinstance(d["object_storage"], list)
        assert len(d["object_storage"]) == 2

    async def test_direct_mount_flags_locality_and_empty_s3fs_path(self) -> None:
        """s3fs_executable_path、object_storage_direct_mount、locality。"""
        d = _new_sandbox_minimal(
            object_storage_direct_mount=False,
            s3fs_executable_path="",
            locality={"region": "ap-southeast", "force": False},
        ).to_dict()
        assert d["object_storage_direct_mount"] is False
        assert d["s3fs_executable_path"] == ""
        assert d["locality"] == {"region": "ap-southeast", "force": False}

    async def test_locality_auto_detect(self) -> None:
        """locality.auto_detect。"""
        d = _new_sandbox_minimal(locality={"auto_detect": True}).to_dict()
        assert d["locality"] == {"auto_detect": True}

    async def test_locality_ap_southeast_force_false(self) -> None:
        """oss_quick_guide 示例：``"locality": {"region": "ap-southeast", "force": false}``。"""
        locality = {"region": "ap-southeast", "force": False}
        d = _new_sandbox_minimal(locality=locality).to_dict()
        assert "locality" in d
        assert d["locality"] == locality
        assert d["locality"]["region"] == "ap-southeast"
        assert d["locality"]["force"] is False

    async def test_omits_unset_optional_fields(self) -> None:
        """未设置的 OSS 相关字段不应出现在 payload。"""
        d = _new_sandbox_minimal().to_dict()
        assert "s3fs_executable_path" not in d
        assert "object_storage_direct_mount" not in d
        assert "locality" not in d
        assert "object_storage" not in d

    async def test_from_dict_roundtrip_preserves_new_fields(self) -> None:
        """from_dict / to_dict 往返保留新字段。"""
        src = {
            "template": "nginx",
            "timeout": 300,
            "object_storage": [
                {"uri": "s3://b/", "mount_point": "/mnt/a", "region": "r"}
            ],
            "object_storage_direct_mount": False,
            "s3fs_executable_path": "",
            "locality": {"region": "ap-southeast", "force": False},
        }
        parsed = NewSandbox.from_dict(src)
        back = parsed.to_dict()
        assert back["template"] == "nginx"
        assert back["object_storage_direct_mount"] is False
        assert back["s3fs_executable_path"] == ""
        assert back["locality"]["region"] == "ap-southeast"
        assert back["locality"]["force"] is False

    # ======================== Scalebox 真实创建（AsyncSandbox.create） ========================

    async def test_async_sandbox_create_with_oss_options(self) -> None:
        """
        按与上文 JSON 用例对应的多 **场景** 各创建 **一台** Scalebox 沙箱；远程 **不** ``kill``。

        无 S3 凭证时仅创建：minimal、``locality`` ap-southeast、``locality`` auto_detect。

        有 ``S3FS_ACCESS_KEY`` / ``S3FS_SECRET_KEY`` 时再创建：单 object_storage、多 object_storage、
        直挂（``object_storage_direct_mount`` + 空 ``s3fs_executable_path``）等。

        每次创建后仅 ``_close_sandbox_local_clients``，避免 “Unclosed client session”。

        未设置 ``SBX_API_KEY`` 或 ``SCALEBOX_SKIP_LIVE_CREATE=1`` 时跳过整段。

        Live 创建遇 **502/503/504** 网关超时会自动重试（默认 4 次，退避；可用
        ``OSS_LIVE_CREATE_MAX_ATTEMPTS``、``OSS_LIVE_CREATE_RETRY_DELAY_S`` 调整）。
        """
        if os.getenv("SCALEBOX_SKIP_LIVE_CREATE", "").strip().lower() in (
            "1",
            "true",
            "yes",
        ):
            logger.info("Skip live AsyncSandbox.create (SCALEBOX_SKIP_LIVE_CREATE is set)")
            return
        if not os.getenv("SBX_API_KEY"):
            logger.info(
                "Skip live AsyncSandbox.create (set SBX_API_KEY to run against Scalebox API)"
            )
            return

        ak = os.getenv("S3FS_ACCESS_KEY")
        sk = os.getenv("S3FS_SECRET_KEY")
        template = os.getenv("OSS_DIRECT_MOUNT_TEMPLATE", "nginx")
        uri = os.getenv("S3FS_TEST_URI", "s3://scalex-packages/test/")
        uri2 = os.getenv("S3FS_TEST_URI_2", "s3://scalex-packages/test/ttttt/")
        region = os.getenv("S3FS_TEST_REGION", "us-east-2")
        endpoint = os.getenv("S3FS_TEST_ENDPOINT", "")

        _region = os.getenv("OSS_LOCALITY_REGION", "ap-southeast")
        _force_env = os.getenv("OSS_LOCALITY_FORCE")
        if _force_env is None:
            locality_default: Dict[str, Any] = {"region": _region, "force": False}
        else:
            locality_default = {
                "region": _region,
                "force": _force_env.strip().lower() in ("1", "true", "yes"),
            }

        def _meta(scenario: str) -> Dict[str, str]:
            return {
                "test": "oss_scalebox_live",
                "suite": "oss_direct_mount",
                "scenario": scenario,
            }

        scenarios: List[Tuple[str, Dict[str, Any]]] = [
            (
                "minimal_no_optional",
                {
                    "template": template,
                    "timeout": 600,
                    "metadata": _meta("minimal_no_optional"),
                },
            ),
            (
                "locality_ap_southeast_force_false",
                {
                    "template": template,
                    "timeout": 600,
                    "metadata": _meta("locality_ap_southeast_force_false"),
                    "locality": {"region": "ap-southeast", "force": False},
                },
            ),
            (
                "locality_auto_detect",
                {
                    "template": template,
                    "timeout": 600,
                    "metadata": _meta("locality_auto_detect"),
                    "locality": {"auto_detect": True},
                },
            ),
        ]

        if ak and sk:
            scenarios.extend(
                [
                    (
                        "single_object_storage_dict_endpoint",
                        {
                            "template": template,
                            "timeout": 600,
                            "metadata": _meta("single_object_storage_dict_endpoint"),
                            "locality": locality_default,
                            "object_storage": {
                                "uri": uri,
                                "mount_point": "/mnt/oss",
                                "access_key": ak,
                                "secret_key": sk,
                                "region": region,
                                "endpoint": endpoint,
                            },
                        },
                    ),
                    (
                        "multi_object_storage_list",
                        {
                            "template": template,
                            "timeout": 600,
                            "metadata": _meta("multi_object_storage_list"),
                            "locality": locality_default,
                            "object_storage": [
                                {
                                    "uri": uri,
                                    "mount_point": "/mnt/oss",
                                    "access_key": ak,
                                    "secret_key": sk,
                                    "region": region,
                                    "endpoint": endpoint,
                                },
                                {
                                    "uri": uri2,
                                    "mount_point": "/mnt/oss-ttttt",
                                    "access_key": ak,
                                    "secret_key": sk,
                                    "region": region,
                                    "endpoint": endpoint,
                                },
                            ],
                        },
                    ),
                    (
                        "direct_mount_s3fs_path_locality",
                        {
                            "template": template,
                            "timeout": 600,
                            "metadata": _meta("direct_mount_s3fs_path_locality"),
                            "locality": {"region": "ap-southeast", "force": False},
                            "object_storage": {
                                "uri": uri,
                                "mount_point": "/mnt/oss",
                                "access_key": ak,
                                "secret_key": sk,
                                "region": region,
                                "endpoint": endpoint,
                            },
                            "object_storage_direct_mount": False,
                            "s3fs_executable_path": os.getenv(
                                "OSS_S3FS_EXECUTABLE_PATH", ""
                            ),
                        },
                    ),
                ]
            )
        else:
            logger.info(
                "S3FS_ACCESS_KEY/S3FS_SECRET_KEY not set: skip live scenarios "
                "that need object_storage (3 locality-only sandboxes still created)"
            )

        created: List[Tuple[str, str]] = []
        failures: List[Tuple[str, str]] = []

        for scenario_name, create_kw in scenarios:
            try:
                sandbox = await _async_sandbox_create_live(create_kw)
                assert sandbox.sandbox_id
                created.append((scenario_name, sandbox.sandbox_id))
                logger.info(
                    "Live [%s] sandbox_id=%s (remote kept; local clients closing)",
                    scenario_name,
                    sandbox.sandbox_id,
                )
                await _close_sandbox_local_clients(sandbox)
            except Exception as e:
                logger.exception("Live scenario %s failed", scenario_name)
                failures.append((scenario_name, str(e)))

        logger.info(
            "Live create finished: %d sandboxes, ids=%s",
            len(created),
            created,
        )
        if failures:
            raise RuntimeError(f"Live create failures: {failures}")

    # ======================== 主测试执行器 ========================

    async def run_all_tests(self) -> None:
        logger.info("开始 Sandbox OSS direct mount create body 验证...")

        await self.run_test(
            self.test_single_object_storage_dict_with_endpoint,
            "Single object_storage dict with endpoint",
        )
        await self.run_test(
            self.test_multi_object_storage_list,
            "Multi object_storage list",
        )
        await self.run_test(
            self.test_direct_mount_flags_locality_and_empty_s3fs_path,
            "Direct mount flags, locality, empty s3fs path",
        )
        await self.run_test(
            self.test_locality_auto_detect,
            "Locality auto_detect",
        )
        await self.run_test(
            self.test_locality_ap_southeast_force_false,
            "Locality region ap-southeast force false (guide)",
        )
        await self.run_test(
            self.test_omits_unset_optional_fields,
            "Omits unset OSS optional fields",
        )
        await self.run_test(
            self.test_from_dict_roundtrip_preserves_new_fields,
            "from_dict roundtrip preserves new fields",
        )
        await self.run_test(
            self.test_async_sandbox_create_with_oss_options,
            "AsyncSandbox.create multi-scenario live (no kill, close local clients)",
        )

    async def cleanup(self) -> None:
        """当前用例无额外资源；预留与 comprehensive 一致。"""
        logger.info("SandboxOssDirectMountValidator cleanup done")

    def print_summary(self) -> None:
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        total_duration = sum(r["duration"] for r in self.test_results)

        print("\n" + "=" * 60)
        print("Sandbox OSS direct mount create body 验证报告")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过数: {passed_tests}")
        print(f"失败数: {failed_tests}")
        print(f"总耗时: {total_duration:.3f}秒")
        if total_tests:
            print(f"成功率: {(passed_tests / total_tests * 100):.1f}%")
        if self.failed_tests:
            print("\n失败的测试:")
            for name in self.failed_tests:
                print(f"  ❌ {name}")
        print("=" * 60)


async def main() -> None:
    validator = SandboxOssDirectMountValidator()
    try:
        await validator.run_all_tests()
    finally:
        await validator.cleanup()
        validator.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
