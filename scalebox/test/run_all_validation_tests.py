#!/usr/bin/env python3
"""
统一的测试运行器 - 运行所有沙箱验证测试

这个脚本会依次运行所有的验证测试，并生成综合报告。
支持选择性运行特定测试套件，并提供详细的性能和结果统计。
"""

import asyncio
import logging
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/home/ubuntu/git_home/scalebox/test/test_results.log"),
    ],
)
logger = logging.getLogger(__name__)


class TestSuiteRunner:
    """测试套件运行器"""

    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.total_start_time = time.time()

    def run_test_module(self, module_name: str, description: str) -> Dict[str, Any]:
        """运行单个测试模块"""
        logger.info(f"\n{'='*60}")
        logger.info(f"开始运行: {description}")
        logger.info(f"模块: {module_name}")
        logger.info(f"{'='*60}")

        start_time = time.time()
        result = {
            "module": module_name,
            "description": description,
            "success": False,
            "duration": 0,
            "error": None,
            "details": {},
        }

        try:
            if module_name == "test_sandbox_async_comprehensive":
                from test_sandbox_async_comprehensive import AsyncSandboxValidator

                validator = AsyncSandboxValidator()
                asyncio.run(validator.run_all_tests())
                result["details"] = {
                    "total_tests": len(validator.test_results),
                    "passed": sum(1 for r in validator.test_results if r["success"]),
                    "failed": len(validator.failed_tests),
                    "test_results": validator.test_results,
                }

            elif module_name == "test_sandbox_sync_comprehensive":
                from test_sandbox_sync_comprehensive import SandboxValidator

                validator = SandboxValidator()
                validator.run_all_tests()
                result["details"] = {
                    "total_tests": len(validator.test_results),
                    "passed": sum(1 for r in validator.test_results if r["success"]),
                    "failed": len(validator.failed_tests),
                    "test_results": validator.test_results,
                }

            elif module_name == "test_sandbox_stress_and_edge_cases":
                from test_sandbox_stress_and_edge_cases import StressTestValidator

                validator = StressTestValidator()
                validator.run_all_tests()
                result["details"] = {
                    "total_tests": len(validator.test_results),
                    "passed": sum(1 for r in validator.test_results if r["success"]),
                    "failed": len(validator.failed_tests),
                    "test_results": validator.test_results,
                }

            elif module_name == "test_sandbox_usage_examples":
                # 使用示例不返回测试结果，只是演示
                import test_sandbox_usage_examples

                test_sandbox_usage_examples.main()
                result["details"] = {
                    "total_tests": 1,
                    "passed": 1,
                    "failed": 0,
                    "note": "Usage examples completed successfully",
                }

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            logger.error(f"测试模块 {module_name} 运行失败: {e}")
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")

        result["duration"] = time.time() - start_time

        # 打印模块结果摘要
        if result["success"]:
            logger.info(f"✅ {description} - 完成")
            if "total_tests" in result["details"]:
                logger.info(f"   总测试: {result['details']['total_tests']}")
                logger.info(f"   通过: {result['details']['passed']}")
                logger.info(f"   失败: {result['details']['failed']}")
            logger.info(f"   耗时: {result['duration']:.3f}秒")
        else:
            logger.error(f"❌ {description} - 失败")
            logger.error(f"   错误: {result['error']}")
            logger.error(f"   耗时: {result['duration']:.3f}秒")

        return result

    def run_all_tests(self, selected_tests: List[str] = None) -> Dict[str, Any]:
        """运行所有或选定的测试"""
        logger.info("ScaleBox 沙箱验证测试套件")
        logger.info(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 定义所有测试套件
        test_suites = [
            {
                "module": "test_sandbox_async_comprehensive",
                "description": "AsyncSandbox 综合功能验证",
            },
            {
                "module": "test_sandbox_sync_comprehensive",
                "description": "Sandbox 综合功能验证",
            },
            {
                "module": "test_sandbox_stress_and_edge_cases",
                "description": "压力测试和边界条件验证",
            },
            {
                "module": "test_sandbox_usage_examples",
                "description": "使用示例和最佳实践演示",
            },
        ]

        # 过滤选定的测试
        if selected_tests:
            test_suites = [
                suite for suite in test_suites if suite["module"] in selected_tests
            ]

        logger.info(f"将运行 {len(test_suites)} 个测试套件")

        # 运行所有测试套件
        for suite in test_suites:
            result = self.run_test_module(suite["module"], suite["description"])
            self.results[suite["module"]] = result

        # 生成综合报告
        total_duration = time.time() - self.total_start_time
        return self.generate_final_report(total_duration)

    def generate_final_report(self, total_duration: float) -> Dict[str, Any]:
        """生成最终测试报告"""
        logger.info(f"\n{'='*80}")
        logger.info("ScaleBox 沙箱验证测试 - 最终报告")
        logger.info(f"{'='*80}")

        # 统计总体结果
        total_suites = len(self.results)
        successful_suites = sum(1 for r in self.results.values() if r["success"])
        failed_suites = total_suites - successful_suites

        total_tests = sum(
            r["details"].get("total_tests", 0) for r in self.results.values()
        )
        total_passed = sum(r["details"].get("passed", 0) for r in self.results.values())
        total_failed = sum(r["details"].get("failed", 0) for r in self.results.values())

        logger.info(f"测试套件统计:")
        logger.info(f"  总套件数: {total_suites}")
        logger.info(f"  成功套件: {successful_suites}")
        logger.info(f"  失败套件: {failed_suites}")
        logger.info(f"  套件成功率: {(successful_suites/total_suites*100):.1f}%")

        logger.info(f"\n测试用例统计:")
        logger.info(f"  总测试数: {total_tests}")
        logger.info(f"  通过测试: {total_passed}")
        logger.info(f"  失败测试: {total_failed}")
        logger.info(
            f"  测试成功率: {(total_passed/total_tests*100):.1f}%"
            if total_tests > 0
            else "  测试成功率: N/A"
        )

        logger.info(f"\n性能统计:")
        logger.info(f"  总运行时间: {total_duration:.3f}秒")

        # 详细结果
        logger.info(f"\n详细结果:")
        for module, result in self.results.items():
            status = "✅ 成功" if result["success"] else "❌ 失败"
            logger.info(f"  {result['description']}: {status}")
            logger.info(f"    模块: {module}")
            logger.info(f"    耗时: {result['duration']:.3f}秒")

            if "total_tests" in result["details"]:
                logger.info(
                    f"    测试: {result['details']['passed']}/{result['details']['total_tests']}"
                )

            if not result["success"] and result["error"]:
                logger.info(f"    错误: {result['error']}")

        # 失败的测试详情
        if failed_suites > 0:
            logger.info(f"\n失败的测试套件:")
            for module, result in self.results.items():
                if not result["success"]:
                    logger.info(f"  ❌ {result['description']}")
                    logger.info(f"     错误: {result['error']}")

        # 性能对比（如果有同步和异步测试结果）
        if (
            "test_sandbox_async_comprehensive" in self.results
            and "test_sandbox_sync_comprehensive" in self.results
        ):
            async_duration = self.results["test_sandbox_async_comprehensive"][
                "duration"
            ]
            sync_duration = self.results["test_sandbox_sync_comprehensive"]["duration"]

            logger.info(f"\n同步 vs 异步性能对比:")
            logger.info(f"  异步版本耗时: {async_duration:.3f}秒")
            logger.info(f"  同步版本耗时: {sync_duration:.3f}秒")

            if async_duration > 0 and sync_duration > 0:
                if async_duration < sync_duration:
                    speedup = sync_duration / async_duration
                    logger.info(f"  异步版本快 {speedup:.1f}x")
                else:
                    speedup = async_duration / sync_duration
                    logger.info(f"  同步版本快 {speedup:.1f}x")

        logger.info(f"\n{'='*80}")
        logger.info(f"测试完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*80}")

        # 返回汇总报告
        summary = {
            "total_suites": total_suites,
            "successful_suites": successful_suites,
            "failed_suites": failed_suites,
            "suite_success_rate": (
                (successful_suites / total_suites * 100) if total_suites > 0 else 0
            ),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "test_success_rate": (
                (total_passed / total_tests * 100) if total_tests > 0 else 0
            ),
            "total_duration": total_duration,
            "results": self.results,
        }

        return summary


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="ScaleBox 沙箱验证测试套件")
    parser.add_argument(
        "--tests",
        nargs="+",
        choices=[
            "test_sandbox_async_comprehensive",
            "test_sandbox_sync_comprehensive",
            "test_sandbox_stress_and_edge_cases",
            "test_sandbox_usage_examples",
        ],
        help="选择要运行的测试套件",
    )
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    parser.add_argument("--output", help="输出报告到文件")

    args = parser.parse_args()

    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    try:
        # 运行测试
        runner = TestSuiteRunner()
        summary = runner.run_all_tests(args.tests)

        # 保存报告到文件
        if args.output:
            import json

            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"测试报告已保存到: {args.output}")

        # 根据测试结果设置退出码
        if summary["failed_suites"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        logger.info("用户中断测试")
        sys.exit(2)
    except Exception as e:
        logger.error(f"测试运行器出现异常: {e}")
        logger.error(traceback.format_exc())
        sys.exit(3)


if __name__ == "__main__":
    main()
