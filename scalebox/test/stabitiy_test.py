#!/usr/bin/env python3
"""
稳定性测试脚本 - 并发执行CodeInterpreter验证测试
"""

import concurrent.futures
import time
import json
import logging
import threading
from typing import List, Dict, Any
import sys
import argparse

# 导入原始测试代码
from code_interpreter_validator import CodeInterpreterValidator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
)
logger = logging.getLogger(__name__)


class StabilityTester:
    """稳定性测试器"""

    def __init__(self, concurrency: int = 10):
        self.concurrency = concurrency
        self.results = []
        self.lock = threading.Lock()
        self.test_counter = 0
        self.total_tests = 0

    def get_test_methods(self) -> List[str]:
        """获取所有测试方法"""
        validator = CodeInterpreterValidator()
        test_methods = []

        # 获取所有以test_开头的方法
        for method_name in dir(validator):
            if method_name.startswith('test_') and callable(getattr(validator, method_name)):
                test_methods.append(method_name)

        self.total_tests = len(test_methods)
        logger.info(f"发现 {self.total_tests} 个测试方法")
        return test_methods

    def run_single_test(self, test_name: str) -> Dict[str, Any]:
        """运行单个测试"""
        thread_name = threading.current_thread().name
        test_id = 0

        with self.lock:
            self.test_counter += 1
            test_id = self.test_counter

        logger.info(f"[线程 {thread_name}] 开始执行测试 {test_id}/{self.total_tests}: {test_name}")

        start_time = time.time()
        success = False
        error_message = ""
        duration = 0

        try:
            # 为每个测试创建独立的验证器实例
            validator = CodeInterpreterValidator()

            # 运行沙箱创建测试
            validator.test_code_interpreter_creation()

            # 运行目标测试
            test_method = getattr(validator, test_name)
            test_method()

            duration = time.time() - start_time
            success = True
            logger.info(f"[线程 {thread_name}] ✅ 测试通过: {test_name} ({duration:.3f}s)")

        except Exception as e:
            duration = time.time() - start_time
            error_message = str(e)
            logger.error(f"[线程 {thread_name}] ❌ 测试失败: {test_name} - {error_message} ({duration:.3f}s)")

        finally:
            # 清理资源
            try:
                if 'validator' in locals():
                    validator.cleanup()
            except Exception as cleanup_error:
                logger.warning(f"[线程 {thread_name}] 清理资源时出错: {cleanup_error}")

        result = {
            'test_id': test_id,
            'test_name': test_name,
            'thread_name': thread_name,
            'success': success,
            'error_message': error_message,
            'duration': duration,
            'timestamp': time.time()
        }

        with self.lock:
            self.results.append(result)

        return result

    def run_concurrent_tests(self) -> Dict[str, Any]:
        """运行并发测试"""
        test_methods = self.get_test_methods()

        if not test_methods:
            logger.error("未发现测试方法")
            return {}

        logger.info(f"开始稳定性测试，并发数: {self.concurrency}")
        logger.info(f"总测试数: {len(test_methods)}")

        start_time = time.time()

        # 使用线程池执行并发测试
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.concurrency,
                thread_name_prefix='TestWorker'
        ) as executor:

            # 提交所有测试任务
            future_to_test = {
                executor.submit(self.run_single_test, test_name): test_name
                for test_name in test_methods
            }

            # 等待所有测试完成
            completed = 0
            for future in concurrent.futures.as_completed(future_to_test):
                test_name = future_to_test[future]
                try:
                    future.result()
                except Exception as exc:
                    logger.error(f"测试 {test_name} 生成异常: {exc}")
                completed += 1
                logger.info(f"测试进度: {completed}/{len(test_methods)}")

        total_duration = time.time() - start_time

        # 生成测试报告
        report = self.generate_report(total_duration)

        return report

    def generate_report(self, total_duration: float) -> Dict[str, Any]:
        """生成测试报告"""
        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]

        total_tests = len(self.results)
        success_count = len(successful_tests)
        failure_count = len(failed_tests)
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0

        # 计算统计信息
        durations = [r['duration'] for r in self.results]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0

        report = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': success_count,
                'failed_tests': failure_count,
                'success_rate': round(success_rate, 2),
                'total_duration': round(total_duration, 3),
                'concurrency': self.concurrency,
                'avg_duration_per_test': round(avg_duration, 3),
                'max_duration': round(max_duration, 3),
                'min_duration': round(min_duration, 3)
            },
            'successful_tests': [
                {
                    'test_name': r['test_name'],
                    'duration': round(r['duration'], 3),
                    'thread': r['thread_name']
                } for r in successful_tests
            ],
            'failed_tests': [
                {
                    'test_name': r['test_name'],
                    'error': r['error_message'],
                    'duration': round(r['duration'], 3),
                    'thread': r['thread_name']
                } for r in failed_tests
            ],
            'execution_timeline': [
                {
                    'test_id': r['test_id'],
                    'test_name': r['test_name'],
                    'thread': r['thread_name'],
                    'success': r['success'],
                    'duration': round(r['duration'], 3),
                    'timestamp': r['timestamp']
                } for r in self.results
            ]
        }

        return report

    def print_detailed_report(self, report: Dict[str, Any]):
        """打印详细报告"""
        summary = report['summary']

        print("\n" + "=" * 80)
        print("🚀 CODEINTERPRETER 稳定性测试报告")
        print("=" * 80)

        print(f"\n📊 测试摘要:")
        print(f"   总测试数:     {summary['total_tests']}")
        print(f"   通过测试:     {summary['successful_tests']} ✅")
        print(f"   失败测试:     {summary['failed_tests']} ❌")
        print(f"   成功率:       {summary['success_rate']}%")
        print(f"   总执行时间:   {summary['total_duration']}s")
        print(f"   并发数:       {summary['concurrency']}")
        print(f"   平均测试时间: {summary['avg_duration_per_test']}s")
        print(f"   最长测试时间: {summary['max_duration']}s")
        print(f"   最短测试时间: {summary['min_duration']}s")

        # 打印成功测试
        if report['successful_tests']:
            print(f"\n✅ 通过的测试 ({len(report['successful_tests'])}):")
            for test in report['successful_tests']:
                print(f"   - {test['test_name']} ({test['duration']}s) [{test['thread']}]")

        # 打印失败测试
        if report['failed_tests']:
            print(f"\n❌ 失败的测试 ({len(report['failed_tests'])}):")
            for test in report['failed_tests']:
                print(f"   - {test['test_name']}")
                print(f"     错误: {test['error']}")
                print(f"     时间: {test['duration']}s")
                print(f"     线程: {test['thread']}")

        # 打印执行时间线
        print(f"\n⏰ 执行时间线:")
        for execution in sorted(report['execution_timeline'], key=lambda x: x['timestamp']):
            status = "✅" if execution['success'] else "❌"
            print(f"   {status} [{execution['thread']}] {execution['test_name']} ({execution['duration']}s)")

        print("\n" + "=" * 80)

        # 保存详细报告到文件
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"stability_test_report_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"📄 详细报告已保存至: {filename}")
        print("=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CodeInterpreter稳定性测试')
    parser.add_argument(
        '--concurrency',
        type=int,
        default=10,
        help='并发线程数 (默认: 10)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )

    args = parser.parse_args()

    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    logger.info(f"启动稳定性测试，并发数: {args.concurrency}")

    tester = StabilityTester(concurrency=args.concurrency)

    try:
        report = tester.run_concurrent_tests()
        tester.print_detailed_report(report)

        # 根据成功率返回适当的退出码
        success_rate = report['summary']['success_rate']
        if success_rate >= 95:
            logger.info(f"🎉 测试成功! 成功率: {success_rate}%")
            sys.exit(0)
        elif success_rate >= 80:
            logger.warning(f"⚠️  测试基本通过，但有改进空间。成功率: {success_rate}%")
            sys.exit(0)
        else:
            logger.error(f"💥 测试失败! 成功率: {success_rate}%")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()