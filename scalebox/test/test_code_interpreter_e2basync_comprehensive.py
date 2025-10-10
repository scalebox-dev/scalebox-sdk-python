#!/usr/bin/env python3
"""
Comprehensive validation test for code_interpreter async module.

This test suite demonstrates and validates all key functionality of the AsyncCodeInterpreter:
- Basic async code execution (Python, shell commands)
- Async callback handling (stdout, stderr, result, error)
- Context management (create, persist, destroy)
- Error handling and edge cases
- Performance testing with concurrency
- Different data types and formats
"""

import asyncio
import datetime
import logging
import os
import time
import json
from typing import List, Optional, Dict, Any
from e2b_code_interpreter import Sandbox

from scalebox.code_interpreter import (
    AsyncSandbox,
    Context,
    Execution,
    ExecutionError,
    Result,
    OutputMessage,
    Logs,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AsyncCodeInterpreterValidator:
    """Comprehensive AsyncCodeInterpreter validation test suite."""

    def __init__(self):
        self.sandbox: Optional[AsyncSandbox] = None
        self.test_results = []
        self.failed_tests = []
        self.contexts: Dict[str, Context] = {}

    async def log_test_result(
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

    async def run_test(self, test_func, test_name: str):
        """运行单个测试并记录结果"""
        start_time = time.time()
        try:
            await test_func()
            duration = time.time() - start_time
            await self.log_test_result(test_name, True, duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test_result(test_name, False, str(e), duration=duration)

    # ======================== 基础异步代码解释器操作测试 ========================

    async def test_async_code_interpreter_creation(self):
        """测试异步代码解释器创建"""
        self.sandbox = await AsyncSandbox.create(
            template="code-interpreter",
            timeout=3600,
            debug=True,
            metadata={"test": "async_code_interpreter_validation"},
            envs={"CI_TEST": "async_test"},
        )
        # time.sleep(5)
        assert self.sandbox is not None
        assert self.sandbox.sandbox_id is not None
        logger.info(
            f"Created AsyncCodeInterpreter sandbox with ID: {self.sandbox.sandbox_id}"
        )

    async def test_basic_async_python_execution(self):
        """测试基础异步Python代码执行"""
        assert self.sandbox is not None

        code = """
import asyncio
import time

print("开始异步Python执行...")

async def async_calculation():
    print("异步计算开始")
    await asyncio.sleep(0.1)  # 模拟异步操作
    result = sum(range(100))
    print(f"异步计算完成: {result}")
    return result

async def main_async():
    task1 = asyncio.create_task(async_calculation())
    task2 = asyncio.create_task(async_calculation())
    
    results = await asyncio.gather(task1, task2)
    print(f"两个异步任务结果: {results}")
    return {"results": results, "sum": sum(results)}

# 运行异步函数
result = await main_async()
print(f"最终结果: {result}")
"""

        execution = await self.sandbox.run_code(code, language="python")
        assert isinstance(execution, Execution)
        assert execution.error is None
        assert len(execution.logs.stdout) > 0
        assert any("异步Python执行" in line for line in execution.logs.stdout)
        logger.info("Async Python execution completed successfully")

    async def test_concurrent_code_execution(self):
        """测试并发代码执行"""
        assert self.sandbox is not None

        codes = [
            """
import asyncio
print(f"任务 1 开始")
await asyncio.sleep(0.1)
result = {"task": 1, "value": 10}
print(f"任务 1 完成: {result}")
result
""",
            """
import asyncio
print(f"任务 2 开始")
await asyncio.sleep(0.1)
result = {"task": 2, "value": 20}
print(f"任务 2 完成: {result}")
result
""",
            """
import asyncio
print(f"任务 3 开始")
await asyncio.sleep(0.1)
result = {"task": 3, "value": 30}
print(f"任务 3 完成: {result}")
result
""",
        ]

        # 并发执行多个代码片段
        start_time = time.time()
        tasks = [self.sandbox.run_code(code, language="python") for code in codes]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        # 验证结果
        assert len(results) == 3
        for execution in results:
            assert execution.error is None
            assert len(execution.logs.stdout) > 0

        logger.info(f"Concurrent execution completed in {duration:.3f}s")
        assert duration < 2.0  # 并发执行应该比串行快

    async def test_async_data_science_workflow(self):
        """测试异步数据科学工作流"""
        assert self.sandbox is not None

        code = """
import asyncio
import pandas as pd
import numpy as np
import json
from concurrent.futures import ThreadPoolExecutor
import time

async def generate_data_async(size, data_type):
    '''异步生成数据'''
    print(f"开始生成 {data_type} 数据，大小: {size}")
    
    # 在线程池中执行CPU密集型操作
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        if data_type == "random":
            data = await loop.run_in_executor(executor, np.random.randn, size)
        elif data_type == "sequence":
            data = await loop.run_in_executor(executor, lambda: np.arange(size))
        else:
            data = await loop.run_in_executor(executor, np.ones, size)
    
    print(f"{data_type} 数据生成完成")
    return data

async def process_data_async(data, name):
    '''异步处理数据'''
    print(f"开始处理数据: {name}")
    
    # 模拟异步处理
    await asyncio.sleep(0.1)
    
    stats = {
        "name": name,
        "mean": float(np.mean(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "size": len(data)
    }
    
    print(f"数据处理完成: {name}")
    return stats

print("开始异步数据科学工作流...")

# 并发生成多个数据集
data_tasks = [
    generate_data_async(1000, "random"),
    generate_data_async(1000, "sequence"),
    generate_data_async(1000, "ones")
]

datasets = await asyncio.gather(*data_tasks)

# 并发处理数据
process_tasks = [
    process_data_async(datasets[0], "随机数据"),
    process_data_async(datasets[1], "序列数据"),
    process_data_async(datasets[2], "常数数据")
]

stats_results = await asyncio.gather(*process_tasks)

print("\\n数据统计结果:")
for stats in stats_results:
    print(f"{stats['name']}: 均值={stats['mean']:.3f}, 标准差={stats['std']:.3f}")

# 创建综合报告
report = {
    "total_datasets": len(datasets),
    "total_datapoints": sum(len(d) for d in datasets),
    "statistics": stats_results,
    "processing_time": "异步并发处理"
}

print(f"\\n工作流完成，处理了 {report['total_datapoints']} 个数据点")
report
"""

        execution = await self.sandbox.run_code(code, language="python")
        assert execution.error is None
        assert any("数据科学工作流" in line for line in execution.logs.stdout)

    # ======================== 异步回调函数测试 ========================

    async def test_async_callback_handling(self):
        """测试异步回调函数处理"""
        assert self.sandbox is not None

        stdout_messages = []
        stderr_messages = []
        results = []
        errors = []

        async def async_stdout_callback(msg: OutputMessage):
            await asyncio.sleep(0.001)  # 模拟异步处理
            stdout_messages.append(msg.content)
            logger.info(f"ASYNC STDOUT: {msg.content}")

        async def async_stderr_callback(msg: OutputMessage):
            await asyncio.sleep(0.001)
            stderr_messages.append(msg.content)
            logger.info(f"ASYNC STDERR: {msg.content}")

        async def async_result_callback(result: Result):
            await asyncio.sleep(0.001)
            results.append(result)
            logger.info(f"ASYNC RESULT: {result}")

        async def async_error_callback(error: ExecutionError):
            await asyncio.sleep(0.001)
            errors.append(error)
            logger.info(f"ASYNC ERROR: {error.name} - {error.value}")

        code = """
import asyncio
import sys

print("异步回调测试开始")

async def async_output_generator():
    for i in range(3):
        print(f"异步输出 {i+1}")
        await asyncio.sleep(0.05)
    
    print("这是标准错误信息", file=sys.stderr)
    
    result = {"status": "completed", "items": 3, "type": "async"}
    print(f"生成结果: {result}")
    return result

result = await async_output_generator()
print("异步回调测试完成")
result
"""

        execution = await self.sandbox.run_code(
            code,
            language="python",
            on_stdout=async_stdout_callback,
            on_stderr=async_stderr_callback,
            on_result=async_result_callback,
            on_error=async_error_callback,
        )

        assert execution.error is None
        logger.info(f"Async callback test completed")

    # ======================== 异步上下文管理测试 ========================

    async def test_async_context_creation(self):
        """测试异步上下文创建"""
        assert self.sandbox is not None

        # 创建Python上下文
        python_context = await self.sandbox.create_code_context(
            language="python", cwd="/tmp"
        )
        assert isinstance(python_context, Context)
        assert python_context.id is not None
        self.contexts["async_python"] = python_context
        logger.info(f"Created async Python context: {python_context.id}")

        # 测试完成后立即清理context
        try:
            await self.sandbox.destroy_context(python_context)
            logger.info(f"Successfully destroyed async context: {python_context.id}")
            # 从contexts字典中移除
            if "async_python" in self.contexts:
                del self.contexts["async_python"]
        except Exception as e:
            logger.warning(f"Failed to destroy async context {python_context.id}: {e}")

    async def test_async_context_state_management(self):
        """测试异步上下文状态管理"""
        assert self.sandbox is not None

        # 创建新的上下文用于状态管理测试
        context = await self.sandbox.create_code_context(language="python", cwd="/tmp")
        self.contexts["async_state_test"] = context

        # 在上下文中设置异步状态
        setup_code = """
import asyncio

# 异步状态变量
async_state = {
    "connections": [],
    "tasks": [],
    "data_cache": {}
}

async def add_connection(conn_id):
    print(f"添加连接: {conn_id}")
    async_state["connections"].append(conn_id)
    await asyncio.sleep(0.01)  # 模拟异步操作
    return len(async_state["connections"])

# 初始化一些连接
connection_count = 0
for i in range(3):
    count = await add_connection(f"conn_{i}")
    connection_count = count

print(f"初始化完成，连接数: {connection_count}")
async_state
"""

        execution1 = await self.sandbox.run_code(setup_code, context=context)
        assert execution1.error is None

        # 在同一上下文中使用已设置的状态
        use_code = """
print(f"当前连接数: {len(async_state['connections'])}")
print(f"连接列表: {async_state['connections']}")

async def process_connections():
    results = []
    for conn in async_state["connections"]:
        print(f"处理连接: {conn}")
        await asyncio.sleep(0.01)
        results.append(f"processed_{conn}")
    return results

processed = await process_connections()
async_state["processed"] = processed

print(f"处理完成: {len(processed)} 个连接")
{"total_connections": len(async_state["connections"]), "processed": len(processed)}
"""

        execution2 = await self.sandbox.run_code(use_code, context=context)
        assert execution2.error is None
        assert any("处理完成" in line for line in execution2.logs.stdout)

        # 测试完成后立即清理context
        try:
            await self.sandbox.destroy_context(context)
            logger.info(f"Successfully destroyed async state context: {context.id}")
            # 从contexts字典中移除
            if "async_state_test" in self.contexts:
                del self.contexts["async_state_test"]
        except Exception as e:
            logger.warning(f"Failed to destroy async state context {context.id}: {e}")

    # ======================== 异步性能测试 ========================

    async def test_async_performance_concurrent_tasks(self):
        """测试异步性能 - 并发任务"""
        assert self.sandbox is not None

        code = """
import asyncio
import time
import random

async def cpu_bound_task(task_id, iterations):
    '''CPU密集型异步任务'''
    print(f"CPU任务 {task_id} 开始，迭代次数: {iterations}")
    
    result = 0
    for i in range(iterations):
        result += i ** 2
        # 定期让出控制权
        if i % 1000 == 0:
            await asyncio.sleep(0)
    
    print(f"CPU任务 {task_id} 完成，结果: {result}")
    return {"task_id": task_id, "result": result, "iterations": iterations}

async def io_bound_task(task_id, delay_time):
    '''IO密集型异步任务'''
    print(f"IO任务 {task_id} 开始，延迟: {delay_time}s")
    
    start = time.time()
    await asyncio.sleep(delay_time)
    duration = time.time() - start
    
    print(f"IO任务 {task_id} 完成，实际耗时: {duration:.3f}s")
    return {"task_id": task_id, "delay": delay_time, "actual_duration": duration}

print("异步性能测试开始...")
overall_start = time.time()

# 创建混合任务：CPU密集型和IO密集型
cpu_tasks = [cpu_bound_task(i, 5000) for i in range(3)]
io_tasks = [io_bound_task(i+10, 0.1 + i*0.05) for i in range(4)]

# 并发执行所有任务
all_tasks = cpu_tasks + io_tasks
results = await asyncio.gather(*all_tasks)

overall_duration = time.time() - overall_start

print(f"\\n性能测试完成:")
print(f"总任务数: {len(results)}")
print(f"CPU任务数: {len(cpu_tasks)}")
print(f"IO任务数: {len(io_tasks)}")
print(f"总执行时间: {overall_duration:.3f}s")

# 分析结果
cpu_results = [r for r in results if "iterations" in r]
io_results = [r for r in results if "delay" in r]

avg_cpu_result = sum(r["result"] for r in cpu_results) / len(cpu_results)
avg_io_duration = sum(r["actual_duration"] for r in io_results) / len(io_results)

print(f"平均CPU任务结果: {avg_cpu_result:.0f}")
print(f"平均IO任务耗时: {avg_io_duration:.3f}s")

{
    "total_tasks": len(results),
    "cpu_tasks": len(cpu_tasks),
    "io_tasks": len(io_tasks),
    "total_time": overall_duration,
    "avg_cpu_result": avg_cpu_result,
    "avg_io_duration": avg_io_duration,
    "concurrency_efficiency": (sum(r["delay"] for r in io_results) / overall_duration) if overall_duration > 0 else 0
}
"""

        start_test_time = time.time()
        execution = await self.sandbox.run_code(code, language="python")
        test_duration = time.time() - start_test_time

        assert execution.error is None
        assert any("性能测试开始" in line for line in execution.logs.stdout)
        logger.info(f"Async performance test completed in {test_duration:.3f}s")

    async def test_async_batch_processing(self):
        """测试异步批处理"""
        assert self.sandbox is not None

        code = """
import asyncio
import json
import time

async def process_batch(batch_id, items):
    '''异步批处理函数'''
    print(f"开始处理批次 {batch_id}，包含 {len(items)} 个项目")
    
    processed_items = []
    start_time = time.time()
    
    for i, item in enumerate(items):
        # 模拟处理每个项目
        processed = {
            "original": item,
            "processed_value": item * 2,
            "batch_id": batch_id,
            "item_index": i
        }
        processed_items.append(processed)
        
        # 每处理几个项目就让出控制权
        if i % 5 == 0:
            await asyncio.sleep(0.01)
    
    processing_time = time.time() - start_time
    print(f"批次 {batch_id} 处理完成，耗时: {processing_time:.3f}s")
    
    return {
        "batch_id": batch_id,
        "item_count": len(items),
        "processed_items": processed_items,
        "processing_time": processing_time
    }

# 准备测试数据
print("准备批处理数据...")
all_data = list(range(100))  # 100个数据项

# 分成多个批次
batch_size = 15
batches = [all_data[i:i+batch_size] for i in range(0, len(all_data), batch_size)]

print(f"数据分为 {len(batches)} 个批次，每批最多 {batch_size} 项")

# 并发处理所有批次
start_time = time.time()
batch_tasks = [process_batch(i, batch) for i, batch in enumerate(batches)]
results = await asyncio.gather(*batch_tasks)
total_time = time.time() - start_time

# 汇总结果
total_items = sum(r["item_count"] for r in results)
avg_batch_time = sum(r["processing_time"] for r in results) / len(results)
throughput = total_items / total_time

print(f"\\n批处理完成:")
print(f"总批次数: {len(results)}")
print(f"总项目数: {total_items}")
print(f"总耗时: {total_time:.3f}s")
print(f"平均批次耗时: {avg_batch_time:.3f}s")
print(f"处理吞吐量: {throughput:.1f} items/s")

{
    "total_batches": len(results),
    "total_items": total_items,
    "total_time": total_time,
    "avg_batch_time": avg_batch_time,
    "throughput": throughput,
    "efficiency": avg_batch_time / total_time * len(results)  # 并发效率指标
}
"""

        execution = await self.sandbox.run_code(code, language="python")
        assert execution.error is None
        assert any("批处理完成" in line for line in execution.logs.stdout)

    # ======================== 异步错误处理测试 ========================

    async def test_async_error_handling(self):
        """测试异步错误处理"""
        assert self.sandbox is not None

        error_captured = []

        async def async_error_callback(error: ExecutionError):
            error_captured.append(error)
            logger.info(f"捕获异步错误: {error.name} - {error.value}")

        # 测试异步错误
        error_code = """
import asyncio

async def failing_task():
    print("开始可能失败的异步任务")
    await asyncio.sleep(0.1)
    
    # 这里会产生一个错误
    result = 10 / 0  # 除零错误
    return result

async def error_handler_demo():
    try:
        result = await failing_task()
        return result
    except Exception as e:
        print(f"在异步函数中捕获错误: {type(e).__name__}: {e}")
        raise  # 重新抛出错误

# 执行会产生错误的异步代码
await error_handler_demo()
"""

        execution = await self.sandbox.run_code(
            error_code, language="python", on_error=async_error_callback
        )
        assert execution.error is not None
        assert "ZeroDivisionError" in execution.error.name
        logger.info("Async error handling test passed")

    # ======================== 异步结果格式测试 ========================

    async def test_async_text_result(self):
        """测试异步文本格式结果"""
        assert self.sandbox is not None

        code = """
import asyncio

# 异步生成纯文本结果
async def generate_async_text():
    await asyncio.sleep(0.1)  # 模拟异步操作
    
    text_content = '''
异步 CodeInterpreter 测试报告
===================================

执行类型: 异步执行
开始时间: 2024-09-17 10:30:00
执行状态: ✅ 异步成功

异步特性验证:
- 支持 async/await 语法
- 并发任务处理能力
- 异步回调机制
- 上下文状态管理

详细描述:
异步CodeInterpreter能够高效处理并发任务，
支持复杂的异步工作流程，提供出色的性能表现。
'''
    return text_content

text_result = await generate_async_text()
print("生成异步文本格式结果")
text_result
"""

        execution = await self.sandbox.run_code(code, language="python")
        assert execution.error is None
        assert len(execution.results) > 0
        logger.info("异步文本格式结果测试完成")

    async def test_async_mixed_format_result(self):
        """测试异步混合格式结果"""
        assert self.sandbox is not None

        code = """
import asyncio
import json
import base64
import matplotlib.pyplot as plt
import numpy as np
import io

async def generate_async_mixed_results():
    print("开始异步生成混合格式结果...")
    
    # 1. 异步文本摘要
    await asyncio.sleep(0.05)
    text_summary = '''
异步 CodeInterpreter 综合测试报告
=====================================

执行模式: 异步并发
完成时间: 2024-09-17 10:30:00
并发任务: 8个
整体状态: ✅ 异步成功

异步特性亮点:
- 高并发处理能力
- 异步资源管理
- 事件驱动架构
- 非阻塞I/O操作
'''
    
    # 2. 异步HTML报告生成
    await asyncio.sleep(0.05)
    html_report = '''
<div class="async-result-report">
    <h2>⚡ 异步 CodeInterpreter 测试完成</h2>
    <div class="status-badge async-success">🚀 异步全部通过</div>
    <div class="async-metrics">
        <div class="metric">
            <label>并发任务:</label>
            <value>8个</value>
        </div>
        <div class="metric">
            <label>平均延迟:</label>
            <value>0.123s</value>
        </div>
        <div class="metric">
            <label>吞吐量:</label>
            <value>65 ops/s</value>
        </div>
    </div>
</div>
'''
    
    # 3. 异步生成图表数据
    await asyncio.sleep(0.05)
    
    # 并发生成多个数据集
    async def generate_chart_data(chart_type):
        await asyncio.sleep(0.02)
        if chart_type == "performance":
            return {
                "type": "line",
                "title": "异步性能趋势",
                "data": {
                    "labels": ["Task1", "Task2", "Task3", "Task4", "Task5"],
                    "values": [92, 95, 88, 97, 94]
                }
            }
        elif chart_type == "concurrency":
            return {
                "type": "bar", 
                "title": "并发执行统计",
                "data": {
                    "labels": ["1并发", "2并发", "4并发", "8并发"],
                    "values": [45, 78, 142, 256]
                }
            }
    
    # 并发生成图表数据
    chart_tasks = [
        generate_chart_data("performance"),
        generate_chart_data("concurrency")
    ]
    chart_data_list = await asyncio.gather(*chart_tasks)
    
    # 4. 异步JSON数据编译
    await asyncio.sleep(0.05)
    json_data = {
        "async_execution": {
            "mode": "concurrent",
            "tasks_completed": 8,
            "success_rate": 100.0,
            "avg_response_time": 0.123
        },
        "performance_summary": {
            "throughput": 65,
            "peak_concurrency": 8,
            "memory_efficient": True,
            "cpu_utilization": "optimal"
        },
        "async_features": [
            "异步任务调度",
            "并发资源管理",
            "事件循环优化",
            "非阻塞I/O处理"
        ],
        "charts": chart_data_list
    }
    
    # 5. 异步Markdown生成
    await asyncio.sleep(0.05)
    markdown_content = '''
## ⚡ 异步 CodeInterpreter 测试总结

### 🎯 异步执行成就
- **完美并发**: 8个任务同时执行
- **零阻塞**: 所有I/O操作非阻塞
- **高吞吐量**: 65 操作/秒
- **资源高效**: CPU和内存使用最优

### 📊 并发性能指标
| 并发级别 | 吞吐量 | 响应时间 | 资源使用 |
|---------|--------|----------|----------|
| 1 | 45 ops/s | 0.022s | 低 |
| 2 | 78 ops/s | 0.025s | 低 |
| 4 | 142 ops/s | 0.028s | 中 |
| 8 | 256 ops/s | 0.031s | 中 |

### 🚀 异步优势
1. **事件驱动**: 基于事件循环的高效调度
2. **资源节约**: 单线程处理多任务
3. **扩展性强**: 轻松应对高并发场景
'''
    
    print("异步混合格式结果生成完成!")
    
    return {
        "formats": ["text", "html", "json", "markdown", "chart"],
        "text": text_summary,
        "html": html_report,
        "json_data": json_data,
        "markdown": markdown_content,
        "charts": chart_data_list,
        "async_summary": {
            "total_formats": 5,
            "concurrent_tasks": 8,
            "execution_mode": "async",
            "performance": "excellent"
        }
    }

# 执行异步混合格式生成
result = await generate_async_mixed_results()
result
"""

        execution = await self.sandbox.run_code(code, language="python")
        assert execution.error is None
        assert any("异步混合格式结果生成完成" in line for line in execution.logs.stdout)
        logger.info("异步混合格式结果测试完成")

    async def test_async_realtime_data_result(self):
        """测试异步实时数据结果"""
        assert self.sandbox is not None

        code = """
import asyncio
import json
import time
from datetime import datetime

class AsyncDataStream:
    def __init__(self):
        self.data_points = []
        self.subscribers = []
    
    async def generate_data_point(self, index):
        '''异步生成单个数据点'''
        await asyncio.sleep(0.02)  # 模拟数据采集延迟
        
        data_point = {
            "id": index,
            "timestamp": datetime.now().isoformat(),
            "value": 50 + 25 * (0.5 - __import__('random').random()),
            "status": "active",
            "metadata": {
                "source": f"sensor_{index % 4}",
                "quality": __import__('random').choice(["high", "medium", "high", "high"])
            }
        }
        return data_point
    
    async def collect_realtime_data(self, duration_seconds=1):
        '''异步收集实时数据流'''
        print(f"开始 {duration_seconds}s 实时数据收集...")
        
        start_time = time.time()
        data_tasks = []
        
        # 创建数据收集任务
        for i in range(20):  # 收集20个数据点
            task = asyncio.create_task(self.generate_data_point(i))
            data_tasks.append(task)
            await asyncio.sleep(0.05)  # 每50ms启动一个任务
        
        # 并发等待所有数据收集完成
        collected_data = await asyncio.gather(*data_tasks)
        collection_time = time.time() - start_time
        
        print(f"数据收集完成，耗时: {collection_time:.3f}s")
        
        return {
            "data_points": collected_data,
            "collection_time": collection_time,
            "total_points": len(collected_data),
            "throughput": len(collected_data) / collection_time
        }
    
    async def process_data_stream(self, raw_data):
        '''异步处理数据流'''
        print("开始异步数据流处理...")
        
        # 并发处理不同的数据分析任务
        async def calculate_statistics():
            await asyncio.sleep(0.1)
            values = [dp["value"] for dp in raw_data["data_points"]]
            return {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }
        
        async def analyze_quality():
            await asyncio.sleep(0.08)
            quality_counts = {}
            for dp in raw_data["data_points"]:
                quality = dp["metadata"]["quality"]
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            return quality_counts
        
        async def detect_anomalies():
            await asyncio.sleep(0.06)
            values = [dp["value"] for dp in raw_data["data_points"]]
            mean_val = sum(values) / len(values)
            threshold = 20  # 异常阈值
            
            anomalies = []
            for dp in raw_data["data_points"]:
                if abs(dp["value"] - mean_val) > threshold:
                    anomalies.append({
                        "id": dp["id"],
                        "value": dp["value"],
                        "deviation": abs(dp["value"] - mean_val)
                    })
            return anomalies
        
        # 并发执行所有分析任务
        stats, quality, anomalies = await asyncio.gather(
            calculate_statistics(),
            analyze_quality(), 
            detect_anomalies()
        )
        
        return {
            "statistics": stats,
            "quality_distribution": quality,
            "anomalies": anomalies,
            "processed_at": datetime.now().isoformat()
        }

# 运行异步实时数据收集和处理
print("启动异步实时数据系统...")
stream = AsyncDataStream()

# 收集数据
raw_data = await stream.collect_realtime_data(1)
print(f"收集了 {raw_data['total_points']} 个数据点")
print(f"数据吞吐量: {raw_data['throughput']:.1f} points/s")

# 处理数据
processed_data = await stream.process_data_stream(raw_data)
print(f"\\n数据处理结果:")
print(f"  平均值: {processed_data['statistics']['mean']:.2f}")
print(f"  数据质量分布: {processed_data['quality_distribution']}")
print(f"  异常数据点: {len(processed_data['anomalies'])} 个")

# 生成实时数据结果
result = {
    "realtime_data": {
        "collection_summary": {
            "total_points": raw_data['total_points'],
            "collection_time": raw_data['collection_time'],
            "throughput": raw_data['throughput']
        },
        "data_analysis": processed_data,
        "raw_samples": raw_data['data_points'][:5],  # 显示前5个样本
        "system_performance": {
            "concurrent_tasks": 20,
            "processing_efficiency": "高效",
            "memory_usage": "优化",
            "async_benefits": [
                "非阻塞数据收集",
                "并发数据处理", 
                "实时流式计算",
                "资源高效利用"
            ]
        }
    }
}

print(f"\\n异步实时数据系统测试完成!")
result
"""

        execution = await self.sandbox.run_code(code, language="python")
        assert execution.error is None
        assert any("异步实时数据系统测试完成" in line for line in execution.logs.stdout)
        logger.info("异步实时数据结果测试完成")

    # ======================== 异步R语言测试 ========================

    async def test_async_r_language_basic_execution(self):
        """测试异步R语言基础执行"""
        assert self.sandbox is not None

        code = """
# 异步R语言基础执行测试
print("Hello from Async R Language!")

# 基础数学运算
x <- 15
y <- 25
sum_result <- x + y
product_result <- x * y

print(paste("Sum:", sum_result))
print(paste("Product:", product_result))

# 向量操作
numbers <- c(2, 4, 6, 8, 10)
mean_value <- mean(numbers)
print(paste("Mean of numbers:", mean_value))

# 数据框创建
df <- data.frame(
  name = c("David", "Emma", "Frank"),
  age = c(28, 32, 26),
  city = c("Paris", "Berlin", "Madrid")
)

print("Data frame created:")
print(df)

# 返回结果
list(
  sum = sum_result,
  product = product_result,
  mean = mean_value,
  data_frame = df
)
"""

        execution = await self.sandbox.run_code(code, language="r")
        assert execution.error is None
        assert any(
            "Hello from Async R Language!" in line for line in execution.logs.stdout
        )
        assert any("Sum:" in line for line in execution.logs.stdout)
        logger.info("Async R language basic execution test passed")

    async def test_async_r_language_data_analysis(self):
        """测试异步R语言数据分析"""
        assert self.sandbox is not None

        code = """
# 异步R语言数据分析测试
library(dplyr)

# 创建示例数据集
set.seed(456)
data <- data.frame(
  id = 1:150,
  value = rnorm(150, mean = 60, sd = 20),
  category = sample(c("X", "Y", "Z"), 150, replace = TRUE),
  score = runif(150, 0, 100)
)

print("Async dataset created with 150 rows")
print(paste("Columns:", paste(names(data), collapse = ", ")))

# 基础统计
summary_stats <- summary(data$value)
print("Summary statistics for value column:")
print(summary_stats)

# 按类别分组统计
grouped_stats <- data %>%
  group_by(category) %>%
  summarise(
    count = n(),
    mean_value = mean(value),
    mean_score = mean(score),
    .groups = 'drop'
  )

print("Grouped statistics:")
print(grouped_stats)

# 数据过滤
high_scores <- data %>%
  filter(score > 85) %>%
  arrange(desc(score))

print(paste("High scores (>85):", nrow(high_scores), "rows"))

# 返回分析结果
list(
  total_rows = nrow(data),
  summary = summary_stats,
  grouped = grouped_stats,
  high_scores_count = nrow(high_scores)
)
"""

        execution = await self.sandbox.run_code(code, language="r")
        assert execution.error is None
        assert any(
            "Async dataset created with 150 rows" in line
            for line in execution.logs.stdout
        )
        assert any("Summary statistics" in line for line in execution.logs.stdout)
        logger.info("Async R language data analysis test passed")

    async def test_async_r_language_visualization(self):
        """测试异步R语言数据可视化"""
        assert self.sandbox is not None

        code = """
# 异步R语言数据可视化测试
library(ggplot2)

# 创建示例数据
set.seed(789)
plot_data <- data.frame(
  x = 1:60,
  y = cumsum(rnorm(60)),
  group = rep(c("GroupA", "GroupB", "GroupC"), each = 20)
)

print("Creating async visualizations...")

# 基础散点图
p1 <- ggplot(plot_data, aes(x = x, y = y)) +
  geom_point() +
  geom_smooth(method = "lm") +
  labs(title = "Async Scatter Plot with Trend Line",
       x = "X Values", y = "Y Values") +
  theme_minimal()

print("Async scatter plot created")

# 分组箱线图
p2 <- ggplot(plot_data, aes(x = group, y = y, fill = group)) +
  geom_boxplot() +
  labs(title = "Async Box Plot by Group",
       x = "Group", y = "Y Values") +
  theme_minimal()

print("Async box plot created")

# 直方图
p3 <- ggplot(plot_data, aes(x = y)) +
  geom_histogram(bins = 25, fill = "lightcoral", alpha = 0.7) +
  labs(title = "Async Distribution of Y Values",
       x = "Y Values", y = "Frequency") +
  theme_minimal()

print("Async histogram created")

# 保存图表信息
plot_info <- list(
  scatter_plot = "Created async scatter plot with trend line",
  box_plot = "Created async box plot by group",
  histogram = "Created async histogram of y values",
  total_plots = 3
)

print("All async visualizations completed successfully")
plot_info
"""

        execution = await self.sandbox.run_code(code, language="r")
        assert execution.error is None
        assert any(
            "Creating async visualizations..." in line for line in execution.logs.stdout
        )
        assert any(
            "All async visualizations completed successfully" in line
            for line in execution.logs.stdout
        )
        logger.info("Async R language visualization test passed")

    async def test_async_r_language_statistics(self):
        """测试异步R语言统计分析"""
        assert self.sandbox is not None

        code = """
# 异步R语言统计分析测试
library(stats)

# 创建两个样本数据
set.seed(101112)
sample1 <- rnorm(120, mean = 15, sd = 3)
sample2 <- rnorm(120, mean = 18, sd = 3.5)

print("Created two async sample datasets")

# 描述性统计
desc_stats1 <- list(
  mean = mean(sample1),
  median = median(sample1),
  sd = sd(sample1),
  min = min(sample1),
  max = max(sample1)
)

desc_stats2 <- list(
  mean = mean(sample2),
  median = median(sample2),
  sd = sd(sample2),
  min = min(sample2),
  max = max(sample2)
)

print("Async descriptive statistics calculated")

# t检验
t_test_result <- t.test(sample1, sample2)
print("Async T-test performed")

# 相关性分析
correlation <- cor(sample1, sample2)
print(paste("Async correlation coefficient:", round(correlation, 4)))

# 线性回归
lm_model <- lm(sample2 ~ sample1)
summary_lm <- summary(lm_model)
print("Async linear regression model fitted")

# 正态性检验
shapiro_test1 <- shapiro.test(sample1[1:50])  # 限制样本大小
shapiro_test2 <- shapiro.test(sample2[1:50])

print("Async normality tests performed")

# 返回统计结果
list(
  sample1_stats = desc_stats1,
  sample2_stats = desc_stats2,
  t_test_p_value = t_test_result$p.value,
  correlation = correlation,
  r_squared = summary_lm$r.squared,
  normality_test1_p = shapiro_test1$p.value,
  normality_test2_p = shapiro_test2$p.value
)
"""

        execution = await self.sandbox.run_code(code, language="r")
        assert execution.error is None
        assert any(
            "Created two async sample datasets" in line
            for line in execution.logs.stdout
        )
        assert any("Async T-test performed" in line for line in execution.logs.stdout)
        logger.info("Async R language statistics test passed")

    async def test_async_r_language_context_management(self):
        """测试异步R语言上下文管理"""
        assert self.sandbox is not None

        # 创建R语言上下文
        r_context = await self.sandbox.create_code_context(language="r", cwd="/tmp")
        self.contexts["async_r_language"] = r_context

        # 在上下文中定义变量和函数
        setup_code = """
# 异步R语言上下文设置
print("Setting up async R language context...")

# 定义全局变量
global_var <- "Hello from Async R Context"
counter <- 0
data_cache <- list()

# 定义函数
increment_counter <- function() {
  counter <<- counter + 1
  return(counter)
}

add_to_cache <- function(key, value) {
  data_cache[[key]] <<- value
  return(length(data_cache))
}

# 初始化一些数据
sample_data <- data.frame(
  x = 1:15,
  y = (1:15) ^ 2
)

print(paste("Async context setup complete. Counter:", counter))
print(paste("Cache size:", length(data_cache)))

# 返回设置信息
list(
  global_var = global_var,
  counter = counter,
  cache_size = length(data_cache),
  data_rows = nrow(sample_data)
)
"""

        execution1 = await self.sandbox.run_code(setup_code, context=r_context)
        assert execution1.error is None
        assert any(
            "Setting up async R language context..." in line
            for line in execution1.logs.stdout
        )

        # 在同一上下文中使用之前定义的变量和函数
        use_code = """
# 使用异步R语言上下文中的变量和函数
print("Using async R language context...")

# 使用全局变量
print(paste("Global variable:", global_var))

# 使用函数
new_counter <- increment_counter()
print(paste("Counter after increment:", new_counter))

# 添加到缓存
cache_size <- add_to_cache("async_test_key", "async_test_value")
print(paste("Cache size after addition:", cache_size))

# 使用数据
data_summary <- summary(sample_data)
print("Data summary:")
print(data_summary)

# 修改数据
sample_data$z <- sample_data$x + sample_data$y
print(paste("Added new column. Total columns:", ncol(sample_data)))

# 返回使用结果
list(
  final_counter = new_counter,
  final_cache_size = cache_size,
  data_columns = ncol(sample_data),
  context_active = TRUE
)
"""

        execution2 = await self.sandbox.run_code(use_code, context=r_context)
        assert execution2.error is None
        assert any(
            "Using async R language context..." in line
            for line in execution2.logs.stdout
        )
        assert any(
            "Counter after increment:" in line for line in execution2.logs.stdout
        )
        logger.info("Async R language context management test passed")

        # 测试完成后立即清理context
        try:
            await self.sandbox.destroy_context(r_context)
            logger.info(f"Successfully destroyed async R context: {r_context.id}")
            # 从contexts字典中移除
            if "async_r_language" in self.contexts:
                del self.contexts["async_r_language"]
        except Exception as e:
            logger.warning(f"Failed to destroy async R context {r_context.id}: {e}")

    # ======================== 异步Node.js/JavaScript 测试 ========================

    async def test_async_nodejs_basic_execution(self):
        """测试异步Node.js基础执行"""
        assert self.sandbox is not None

        code = """
// Node.js 基础执行（异步）
console.log("Hello from Async Node.js Kernel!");
const a = 11, b = 13;
console.log(`Sum: ${a + b}`);
console.log(`Product: ${a * b}`);
({ sum: a + b, product: a * b })
"""

        execution = await self.sandbox.run_code(code, language="javascript")
        assert execution.error is None
        assert any(
            "Hello from Async Node.js Kernel!" in line for line in execution.logs.stdout
        )
        assert any("Sum:" in line for line in execution.logs.stdout)
        logger.info("Async Node.js basic execution test passed")

    async def test_async_nodejs_async_promises(self):
        """测试异步Node.js Promise/async"""
        assert self.sandbox is not None

        code = """
function delay(ms){ return new Promise(r=>setTimeout(r, ms)); }
async function run(){
  console.log("Async tasks start");
  const t0 = Date.now();
  await delay(40);
  const res = await Promise.all([
    (async()=>{ await delay(15); return 21; })(),
    (async()=>{ await delay(25); return 21; })()
  ]);
  const sum = res.reduce((a,b)=>a+b,0);
  const dt = Date.now()-t0;
  console.log(`Async tasks done in ${dt} ms`);
  return { sum, dt };
}
run();
"""

        execution = await self.sandbox.run_code(code, language="javascript")
        assert execution.error is None
        assert any("Async tasks start" in line for line in execution.logs.stdout)
        assert any("Async tasks done" in line for line in execution.logs.stdout)
        logger.info("Async Node.js promises test passed")

    async def test_async_nodejs_data_processing(self):
        """测试异步Node.js数据处理"""
        assert self.sandbox is not None

        code = """
const rows = Array.from({length: 120}, (_, i) => ({ id: i+1, value: Math.round(Math.random()*100), group: ['X','Y','Z'][i%3] }));
const stats = rows.reduce((acc, r)=>{ if(!acc[r.group]) acc[r.group]={count:0,sum:0}; acc[r.group].count++; acc[r.group].sum+=r.value; return acc; }, {});
const out = Object.entries(stats).map(([g,s])=>({ group: g, count: s.count, mean: s.sum/s.count }));
console.log("Async grouped stats ready");
({ total: rows.length, groups: out })
"""

        execution = await self.sandbox.run_code(code, language="javascript")
        assert execution.error is None
        assert any(
            "Async grouped stats ready" in line for line in execution.logs.stdout
        )
        logger.info("Async Node.js data processing test passed")

    async def test_async_nodejs_chart_data(self):
        """测试异步Node.js图表数据生成"""
        assert self.sandbox is not None

        code = """
const labels = Array.from({length: 5}, (_, i)=>`T${i+1}`);
const values = labels.map(()=> Math.round(Math.random()*50+50));
const chart = { type: 'bar', data: { labels, datasets: [{ label: 'Load', data: values, backgroundColor: '#1c7ed6' }] } };
console.log("Async chart data generated");
({ chart })
"""

        execution = await self.sandbox.run_code(code, language="javascript")
        assert execution.error is None
        assert any(
            "Async chart data generated" in line for line in execution.logs.stdout
        )
        assert len(execution.results) > 0
        logger.info("Async Node.js chart data test passed")

    async def test_async_nodejs_context_management(self):
        """测试异步Node.js上下文管理"""
        assert self.sandbox is not None

        # 创建Node.js上下文
        js_context = await self.sandbox.create_code_context(
            language="javascript", cwd="/tmp"
        )
        self.contexts["async_nodejs"] = js_context

        setup = """
console.log("Setup async Node.js context");
globalThis.state = { counter: 0 };
function inc(){ globalThis.state.counter += 1; return globalThis.state.counter; }
({ counter: globalThis.state.counter })
"""

        e1 = await self.sandbox.run_code(setup, context=js_context)
        assert e1.error is None
        assert any("Setup async Node.js context" in line for line in e1.logs.stdout)

        use = """
console.log("Use async Node.js context");
const c1 = inc();
const c2 = inc();
({ after: c2 })
"""

        e2 = await self.sandbox.run_code(use, context=js_context)
        assert e2.error is None
        assert any("Use async Node.js context" in line for line in e2.logs.stdout)

        # 清理上下文
        try:
            await self.sandbox.destroy_context(js_context)
            if "async_nodejs" in self.contexts:
                del self.contexts["async_nodejs"]
            logger.info("Destroyed async Node.js context")
        except Exception as e:
            logger.warning(f"Failed to destroy async Node.js context: {e}")

    # ======================== 异步Bash 测试 ========================

    async def test_async_bash_basic_execution(self):
        """测试异步Bash基础执行"""
        assert self.sandbox is not None

        code = """
echo "Hello from Async Bash Kernel!"
NAME="scalebox"
echo "Hello, ${NAME}!"
whoami
date
"""

        execution = await self.sandbox.run_code(code, language="bash")
        assert execution.error is None
        assert any(
            "Hello from Async Bash Kernel!" in line for line in execution.logs.stdout
        )
        assert any("Hello, scalebox!" in line for line in execution.logs.stdout)
        logger.info("Async Bash basic execution test passed")

    async def test_async_bash_file_operations(self):
        """测试异步Bash文件操作"""
        assert self.sandbox is not None

        code = """
set -e
WORKDIR="/tmp/abash_demo"
mkdir -p "$WORKDIR"
cd "$WORKDIR"
echo "first" > one.txt
echo "second" > two.txt
cat one.txt two.txt > both.txt
ls -l
wc -l both.txt
echo "ABASH_DONE"
"""

        execution = await self.sandbox.run_code(code, language="bash")
        assert execution.error is None
        assert any("ABASH_DONE" in line for line in execution.logs.stdout)
        logger.info("Async Bash file operations test passed")

    async def test_async_bash_pipelines_and_grep(self):
        """测试异步Bash管道与grep"""
        assert self.sandbox is not None

        code = """
printf "%s\n" a b a c a | grep -n "a" | awk -F: '{print "row", $1, ":", $2}'
echo "ABASH_PIPE_OK"
"""

        execution = await self.sandbox.run_code(code, language="bash")
        assert execution.error is None
        assert any("ABASH_PIPE_OK" in line for line in execution.logs.stdout)
        logger.info("Async Bash pipelines/grep test passed")

    async def test_async_bash_env_and_exit_codes(self):
        """测试异步Bash环境变量与退出码"""
        assert self.sandbox is not None

        code = """
export MODE=async
echo "MODE=$MODE"
(exit 9)
echo $?
"""

        execution = await self.sandbox.run_code(code, language="bash")
        assert execution.error is None
        assert any("MODE=async" in line for line in execution.logs.stdout)
        assert any(line.strip() == "9" for line in execution.logs.stdout)
        logger.info("Async Bash env and exit codes test passed")

    async def test_async_bash_context_management(self):
        """测试异步Bash上下文管理"""
        assert self.sandbox is not None

        # 创建Bash上下文
        bash_ctx = await self.sandbox.create_code_context(language="bash", cwd="/tmp")
        self.contexts["async_bash"] = bash_ctx

        setup = """
echo "Setup async Bash context"
COUNT=3
echo $COUNT
"""

        e1 = await self.sandbox.run_code(setup, context=bash_ctx)
        assert e1.error is None
        assert any("Setup async Bash context" in line for line in e1.logs.stdout)

        use = """
echo "Use async Bash context"
COUNT=$((COUNT+2))
echo "COUNT_AFTER=$COUNT"
"""

        e2 = await self.sandbox.run_code(use, context=bash_ctx)
        assert e2.error is None
        assert any("Use async Bash context" in line for line in e2.logs.stdout)
        assert any("COUNT_AFTER=5" in line for line in e2.logs.stdout)

        # 清理上下文
        try:
            await self.sandbox.destroy_context(bash_ctx)
            if "async_bash" in self.contexts:
                del self.contexts["async_bash"]
            logger.info("Destroyed async Bash context")
        except Exception as e:
            logger.warning(f"Failed to destroy async Bash context: {e}")

    # ======================== 异步IJAVA 测试 ========================

    async def test_async_ijava_basic_execution(self):
        """测试异步IJAVA基础执行"""
        assert self.sandbox is not None

        code = """
// 异步IJAVA 基础执行测试
System.out.println("Hello from Async IJAVA Kernel!");

// 基础变量和运算
int x = 15;
int y = 25;
int sum = x + y;
int product = x * y;

System.out.println("Sum: " + sum);
System.out.println("Product: " + product);

// 字符串操作
String name = "AsyncScaleBox";
String greeting = "Hello, " + name + "!";
System.out.println(greeting);

// 数组操作
int[] numbers = {2, 4, 6, 8, 10};
int total = 0;
for (int num : numbers) {
    total += num;
}
System.out.println("Array sum: " + total);

// IJAVA 特色：直接输出变量值
x;
y;
sum;
product;
total;
"""

        execution = await self.sandbox.run_code(code, language="java")
        assert execution.error is None
        assert any(
            "Hello from Async IJAVA Kernel!" in line for line in execution.logs.stdout
        )
        assert any("Sum: 40" in line for line in execution.logs.stdout)
        assert any("Array sum: 30" in line for line in execution.logs.stdout)
        logger.info("Async IJAVA basic execution test passed")

    async def test_async_ijava_oop_features(self):
        """测试异步IJAVA面向对象特性"""
        assert self.sandbox is not None

        code = """
// 异步IJAVA 面向对象特性测试
System.out.println("Testing Async IJAVA OOP features...");

// 定义类
class AsyncPerson {
    private String name;
    private int age;
    
    public AsyncPerson(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() { return name; }
    public int getAge() { return age; }
    
    public void introduce() {
        System.out.println("Hi, I'm " + name + " and I'm " + age + " years old.");
    }
}

class AsyncStudent extends AsyncPerson {
    private String major;
    
    public AsyncStudent(String name, int age, String major) {
        super(name, age);
        this.major = major;
    }
    
    @Override
    public void introduce() {
        super.introduce();
        System.out.println("I'm studying " + major + ".");
    }
}

// 创建对象并测试
AsyncPerson person = new AsyncPerson("Eve", 28);
person.introduce();

AsyncStudent student = new AsyncStudent("Frank", 24, "Data Science");
student.introduce();

// IJAVA 特色：直接输出对象信息
person.getName();
student.getAge();
person;
student;

System.out.println("Async IJAVA OOP test completed successfully!");
"""

        execution = await self.sandbox.run_code(code, language="java")
        assert execution.error is None
        assert any(
            "Testing Async IJAVA OOP features..." in line
            for line in execution.logs.stdout
        )
        assert any("Hi, I'm Eve" in line for line in execution.logs.stdout)
        assert any(
            "I'm studying Data Science" in line for line in execution.logs.stdout
        )
        logger.info("Async IJAVA OOP features test passed")

    async def test_async_ijava_collections(self):
        """测试异步IJAVA集合框架"""
        assert self.sandbox is not None

        code = """
import java.util.*;

System.out.println("Testing Async IJAVA Collections...");

// ArrayList
List<String> colors = new ArrayList<>();
colors.add("Red");
colors.add("Green");
colors.add("Blue");
System.out.println("Colors: " + colors);

// HashMap
Map<String, Integer> ages = new HashMap<>();
ages.put("Alice", 25);
ages.put("Bob", 30);
ages.put("Charlie", 35);
System.out.println("Ages: " + ages);

// HashSet
Set<String> uniqueWords = new HashSet<>();
uniqueWords.add("hello");
uniqueWords.add("world");
uniqueWords.add("hello"); // 重复元素
System.out.println("Unique words: " + uniqueWords);

// 遍历集合
System.out.println("Iterating through colors:");
for (String color : colors) {
    System.out.println("- " + color);
}

// IJAVA 特色：直接输出集合内容
colors;
ages;
uniqueWords;

// 集合操作
colors.size();
ages.containsKey("Alice");
uniqueWords.contains("hello");

System.out.println("Async IJAVA Collections test completed!");
"""

        execution = await self.sandbox.run_code(code, language="java")
        assert execution.error is None
        assert any(
            "Testing Async IJAVA Collections..." in line
            for line in execution.logs.stdout
        )
        assert any(
            "Colors: [Red, Green, Blue]" in line for line in execution.logs.stdout
        )
        assert any(
            "Unique words: [hello, world]" in line for line in execution.logs.stdout
        )
        logger.info("Async IJAVA collections test passed")

    async def test_async_ijava_file_io(self):
        """测试异步IJAVA文件I/O"""
        assert self.sandbox is not None

        code = """
import java.io.*;
import java.nio.file.*;

System.out.println("Testing Async IJAVA File I/O...");

try {
    // 创建临时目录
    Path tempDir = Files.createTempDirectory("async_ijava_demo");
    System.out.println("Created temp directory: " + tempDir);
    
    // 写入文件
    Path filePath = tempDir.resolve("async_test.txt");
    String content = "Hello from Async IJAVA File I/O!\nThis is an async test file.\n";
    Files.write(filePath, content.getBytes());
    System.out.println("File written successfully");
    
    // 读取文件
    String readContent = new String(Files.readAllBytes(filePath));
    System.out.println("File content:");
    System.out.println(readContent);
    
    // 文件信息
    long size = Files.size(filePath);
    System.out.println("File size: " + size + " bytes");
    
    // IJAVA 特色：直接输出文件信息
    filePath;
    size;
    Files.exists(filePath);
    
    // 清理
    Files.delete(filePath);
    Files.delete(tempDir);
    System.out.println("Async IJAVA File I/O test completed successfully!");
    
} catch (IOException e) {
    System.err.println("Error: " + e.getMessage());
}
"""

        execution = await self.sandbox.run_code(code, language="java")
        assert execution.error is None
        assert any(
            "Testing Async IJAVA File I/O..." in line for line in execution.logs.stdout
        )
        assert any(
            "File written successfully" in line for line in execution.logs.stdout
        )
        assert any(
            "Hello from Async IJAVA File I/O!" in line for line in execution.logs.stdout
        )
        logger.info("Async IJAVA file I/O test passed")

    async def test_async_ijava_context_management(self):
        """测试异步IJAVA上下文管理"""
        assert self.sandbox is not None

        # 创建IJAVA上下文
        ijava_context = await self.sandbox.create_code_context(
            language="java", cwd="/tmp"
        )
        self.contexts["async_ijava"] = ijava_context

        # 在上下文中定义类和变量
        setup_code = """
System.out.println("Setting up async IJAVA context...");

// 定义全局变量
int counter = 0;
String message = "Hello from Async IJAVA Context!";

System.out.println("Initial counter: " + counter);
System.out.println("Message: " + message);

// 定义方法
void incrementCounter() {
    counter++;
}

int getCounter() {
    return counter;
}

// 定义类
class AsyncContextDemo {
    private static int staticCounter = 0;
    
    public static void incrementStaticCounter() {
        staticCounter++;
    }
    
    public static int getStaticCounter() {
        return staticCounter;
    }
}

// 测试方法
incrementCounter();
System.out.println("Counter after increment: " + counter);

// IJAVA 特色：直接输出变量值
counter;
message;
getCounter();
"""

        execution1 = await self.sandbox.run_code(setup_code, context=ijava_context)
        assert execution1.error is None
        assert any(
            "Setting up async IJAVA context..." in line
            for line in execution1.logs.stdout
        )
        assert any("Initial counter: 0" in line for line in execution1.logs.stdout)

        # 在同一上下文中使用之前定义的变量和方法
        use_code = """
System.out.println("Using async IJAVA context...");

// 使用之前定义的变量和方法
incrementCounter();
int currentCounter = getCounter();
System.out.println("Current counter: " + currentCounter);

// 使用之前定义的类
AsyncContextDemo.incrementStaticCounter();
int staticCounter = AsyncContextDemo.getStaticCounter();
System.out.println("Static counter: " + staticCounter);

// 创建新变量
String newMessage = "Modified async context data";
System.out.println("New message: " + newMessage);

// IJAVA 特色：直接输出所有变量
counter;
currentCounter;
staticCounter;
newMessage;
AsyncContextDemo.getStaticCounter();

System.out.println("Async IJAVA context usage completed!");
"""

        execution2 = await self.sandbox.run_code(use_code, context=ijava_context)
        assert execution2.error is None
        assert any(
            "Using async IJAVA context..." in line for line in execution2.logs.stdout
        )
        assert any("Current counter: 2" in line for line in execution2.logs.stdout)
        assert any("Static counter: 1" in line for line in execution2.logs.stdout)
        logger.info("Async IJAVA context management test passed")

        # 测试完成后立即清理context
        try:
            await self.sandbox.destroy_context(ijava_context)
            logger.info(
                f"Successfully destroyed async IJAVA context: {ijava_context.id}"
            )
            # 从contexts字典中移除
            if "async_ijava" in self.contexts:
                del self.contexts["async_ijava"]
        except Exception as e:
            logger.warning(
                f"Failed to destroy async IJAVA context {ijava_context.id}: {e}"
            )

    # ======================== 异步Deno 测试 ========================

    async def test_async_deno_basic_execution(self):
        """测试异步Deno基础执行"""
        assert self.sandbox is not None

        code = """
// 异步Deno 基础执行测试
console.log("Hello from Async Deno Kernel!");

// 基础变量和运算
const x: number = 14;
const y: number = 16;
const sum: number = x + y;
const product: number = x * y;

console.log(`Sum: ${sum}`);
console.log(`Product: ${product}`);

// 字符串操作
const name: string = "AsyncDenoScaleBox";
const greeting: string = `Hello, ${name}!`;
console.log(greeting);

// 数组操作
const numbers: number[] = [2, 4, 6, 8, 10];
const total: number = numbers.reduce((acc, num) => acc + num, 0);
console.log(`Array sum: ${total}`);

// 对象操作
const person = {
  name: "Bob",
  age: 30,
  city: "London"
};
console.log(`Person: ${person.name}, ${person.age} years old`);
"""

        execution = await self.sandbox.run_code(code, language="typescript")
        assert execution.error is None
        assert any(
            "Hello from Async Deno Kernel!" in line for line in execution.logs.stdout
        )
        assert any("Sum: 30" in line for line in execution.logs.stdout)
        assert any("Array sum: 30" in line for line in execution.logs.stdout)
        logger.info("Async Deno basic execution test passed")

    async def test_async_deno_typescript_features(self):
        """测试异步Deno TypeScript特性"""
        assert self.sandbox is not None

        code = """
// 异步Deno TypeScript 特性测试
interface AsyncUser {
  id: number;
  name: string;
  email: string;
  isActive: boolean;
}

class AsyncUserManager {
  private users: AsyncUser[] = [];
  
  constructor() {
    console.log("AsyncUserManager initialized");
  }
  
  addUser(user: AsyncUser): void {
    this.users.push(user);
    console.log(`Added user: ${user.name}`);
  }
  
  getUsers(): AsyncUser[] {
    return this.users;
  }
  
  findUserById(id: number): AsyncUser | undefined {
    return this.users.find(user => user.id === id);
  }
}

// 使用泛型
function processAsyncItems<T>(items: T[], processor: (item: T) => void): void {
  items.forEach(processor);
}

// 枚举
enum AsyncStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected"
}

console.log("Testing Async Deno TypeScript features...");

const asyncUserManager = new AsyncUserManager();
asyncUserManager.addUser({
  id: 1,
  name: "Async John",
  email: "async.john@example.com",
  isActive: true
});

asyncUserManager.addUser({
  id: 2,
  name: "Async Jane",
  email: "async.jane@example.com",
  isActive: false
});

const users = asyncUserManager.getUsers();
console.log(`Total users: ${users.length}`);

const foundUser = asyncUserManager.findUserById(1);
console.log(`Found user: ${foundUser?.name}`);

// 使用泛型函数
const numbers = [10, 20, 30, 40, 50];
processAsyncItems(numbers, (num) => console.log(`Processing: ${num}`));

console.log(`Status: ${AsyncStatus.APPROVED}`);
console.log("Async TypeScript features test completed!");
"""

        execution = await self.sandbox.run_code(code, language="typescript")
        assert execution.error is None
        assert any(
            "Testing Async Deno TypeScript features..." in line
            for line in execution.logs.stdout
        )
        assert any("Added user: Async John" in line for line in execution.logs.stdout)
        assert any("Total users: 2" in line for line in execution.logs.stdout)
        logger.info("Async Deno TypeScript features test passed")

    async def test_async_deno_async_await(self):
        """测试异步Deno异步/await"""
        assert self.sandbox is not None

        code = """
// 异步Deno 异步/await 测试
async function asyncDelay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function asyncFetchData(id: number): Promise<{ id: number; data: string }> {
  await asyncDelay(30);
  return { id, data: `Async Data for ID ${id}` };
}

async function asyncProcessBatch(ids: number[]): Promise<string[]> {
  console.log("Starting async batch processing...");
  const start = Date.now();
  
  const results = await Promise.all(
    ids.map(async (id) => {
      const result = await asyncFetchData(id);
      console.log(`Async Processed: ${result.data}`);
      return result.data;
    })
  );
  
  const duration = Date.now() - start;
  console.log(`Async batch processing completed in ${duration}ms`);
  return results;
}

async function asyncMain(): Promise<void> {
  console.log("Testing Async Deno async/await...");
  
  const ids = [1, 2, 3];
  const results = await asyncProcessBatch(ids);
  
  console.log(`Total async results: ${results.length}`);
  console.log("Async async/await test completed!");
}

asyncMain();
"""

        execution = await self.sandbox.run_code(code, language="typescript")
        assert execution.error is None
        assert any(
            "Testing Async Deno async/await..." in line
            for line in execution.logs.stdout
        )
        assert any(
            "Starting async batch processing..." in line
            for line in execution.logs.stdout
        )
        assert any(
            "Async batch processing completed" in line for line in execution.logs.stdout
        )
        logger.info("Async Deno async/await test passed")

    async def test_async_deno_file_operations(self):
        """测试异步Deno文件操作"""
        assert self.sandbox is not None

        code = """
// 异步Deno 文件操作测试
import { ensureDir, writeTextFile, readTextFile, remove } from "https://deno.land/std@0.208.0/fs/mod.ts";

async function asyncFileOperations(): Promise<void> {
  console.log("Testing Async Deno file operations...");
  
  try {
    // 创建临时目录
    const tempDir = "/tmp/async_deno_demo";
    await ensureDir(tempDir);
    console.log(`Created directory: ${tempDir}`);
    
    // 写入文件
    const filePath = `${tempDir}/async_test.txt`;
    const content = "Hello from Async Deno File Operations!\nThis is an async test file.\n";
    await writeTextFile(filePath, content);
    console.log("Async file written successfully");
    
    // 读取文件
    const readContent = await readTextFile(filePath);
    console.log("Async file content:");
    console.log(readContent);
    
    // 文件信息
    const fileInfo = await Deno.stat(filePath);
    console.log(`Async file size: ${fileInfo.size} bytes`);
    console.log(`Async created: ${fileInfo.birthtime}`);
    
    // 清理
    await remove(filePath);
    await remove(tempDir);
    console.log("Async file operations test completed successfully!");
    
  } catch (error) {
    console.error(`Async Error: ${error.message}`);
  }
}

asyncFileOperations();
"""

        execution = await self.sandbox.run_code(code, language="typescript")
        assert execution.error is None
        assert any(
            "Testing Async Deno file operations..." in line
            for line in execution.logs.stdout
        )
        assert any(
            "Async file written successfully" in line for line in execution.logs.stdout
        )
        assert any(
            "Hello from Async Deno File Operations!" in line
            for line in execution.logs.stdout
        )
        logger.info("Async Deno file operations test passed")

    async def test_async_deno_context_management(self):
        """测试异步Deno上下文管理"""
        assert self.sandbox is not None

        # 创建Deno上下文
        deno_context = await self.sandbox.create_code_context(
            language="typescript", cwd="/tmp"
        )
        self.contexts["async_deno"] = deno_context

        # 在上下文中定义变量和函数
        setup_code = """
// 异步Deno 上下文设置
console.log("Setting up async Deno context...");

// 定义全局变量
let asyncCounter: number = 0;
const asyncCache: Map<string, any> = new Map();

// 定义函数
function asyncIncrementCounter(): number {
  asyncCounter++;
  return asyncCounter;
}

function asyncAddToCache(key: string, value: any): number {
  asyncCache.set(key, value);
  return asyncCache.size;
}

// 定义接口
interface AsyncContextData {
  id: number;
  value: string;
}

const asyncContextData: AsyncContextData = {
  id: 1,
  value: "Hello from Async Deno Context!"
};

console.log(`Initial async counter: ${asyncCounter}`);
console.log(`Async cache size: ${asyncCache.size}`);
console.log(`Async context data: ${asyncContextData.value}`);
"""

        execution1 = await self.sandbox.run_code(setup_code, context=deno_context)
        assert execution1.error is None
        assert any(
            "Setting up async Deno context..." in line
            for line in execution1.logs.stdout
        )
        assert any(
            "Initial async counter: 0" in line for line in execution1.logs.stdout
        )

        # 在同一上下文中使用之前定义的变量和函数
        use_code = """
// 使用异步Deno 上下文中的变量和函数
console.log("Using async Deno context...");

// 使用全局变量
console.log(`Current async counter: ${asyncCounter}`);
console.log(`Current async cache size: ${asyncCache.size}`);

// 使用函数
const newAsyncCounter = asyncIncrementCounter();
console.log(`Async counter after increment: ${newAsyncCounter}`);

const newAsyncCacheSize = asyncAddToCache("async_test_key", "async_test_value");
console.log(`Async cache size after addition: ${newAsyncCacheSize}`);

// 使用上下文数据
console.log(`Async context data ID: ${asyncContextData.id}`);
console.log(`Async context data value: ${asyncContextData.value}`);

// 修改上下文数据
asyncContextData.value = "Modified async context data";
console.log(`Modified async context data: ${asyncContextData.value}`);

console.log("Async context usage completed!");
"""

        execution2 = await self.sandbox.run_code(use_code, context=deno_context)
        assert execution2.error is None
        assert any(
            "Using async Deno context..." in line for line in execution2.logs.stdout
        )
        assert any(
            "Async counter after increment: 1" in line
            for line in execution2.logs.stdout
        )
        assert any(
            "Async cache size after addition: 1" in line
            for line in execution2.logs.stdout
        )
        logger.info("Async Deno context management test passed")

        # 测试完成后立即清理context
        try:
            await self.sandbox.destroy_context(deno_context)
            logger.info(f"Successfully destroyed async Deno context: {deno_context.id}")
            # 从contexts字典中移除
            if "async_deno" in self.contexts:
                del self.contexts["async_deno"]
        except Exception as e:
            logger.warning(
                f"Failed to destroy async Deno context {deno_context.id}: {e}"
            )

    # ======================== 高级异步功能测试 ========================

    async def test_async_websocket_simulation(self):
        """测试异步WebSocket模拟"""
        assert self.sandbox is not None

        code = """
import asyncio
import json
import time
from datetime import datetime

class MockWebSocketConnection:
    '''模拟WebSocket连接'''
    def __init__(self, connection_id):
        self.connection_id = connection_id
        self.connected = True
        self.message_queue = asyncio.Queue()
        
    async def send_message(self, message):
        if self.connected:
            await self.message_queue.put({
                "type": "outgoing",
                "data": message,
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(0.01)  # 模拟网络延迟
            return True
        return False
    
    async def receive_message(self):
        if self.connected:
            # 模拟接收消息
            await asyncio.sleep(0.05)  # 模拟等待消息
            return {
                "type": "incoming",
                "data": f"Response from server to {self.connection_id}",
                "timestamp": datetime.now().isoformat()
            }
        return None
    
    async def close(self):
        self.connected = False
        print(f"连接 {self.connection_id} 已关闭")

async def websocket_client(client_id, message_count):
    '''模拟WebSocket客户端'''
    print(f"客户端 {client_id} 开始连接")
    
    connection = MockWebSocketConnection(client_id)
    messages_sent = 0
    messages_received = 0
    
    try:
        # 发送和接收消息
        for i in range(message_count):
            # 发送消息
            message = f"Message {i+1} from client {client_id}"
            success = await connection.send_message(message)
            if success:
                messages_sent += 1
            
            # 接收回复
            response = await connection.receive_message()
            if response:
                messages_received += 1
                print(f"客户端 {client_id} 收到: {response['data'][:50]}...")
    
    finally:
        await connection.close()
    
    return {
        "client_id": client_id,
        "messages_sent": messages_sent,
        "messages_received": messages_received,
        "success_rate": messages_received / messages_sent if messages_sent > 0 else 0
    }

print("开始WebSocket模拟测试...")
start_time = time.time()

# 创建多个并发客户端
client_count = 5
messages_per_client = 3

client_tasks = [
    websocket_client(f"client_{i}", messages_per_client) 
    for i in range(client_count)
]

# 并发运行所有客户端
results = await asyncio.gather(*client_tasks)

end_time = time.time()
total_duration = end_time - start_time

# 汇总统计
total_sent = sum(r["messages_sent"] for r in results)
total_received = sum(r["messages_received"] for r in results)
overall_success_rate = total_received / total_sent if total_sent > 0 else 0

print(f"\\nWebSocket模拟完成:")
print(f"客户端数量: {client_count}")
print(f"每客户端消息: {messages_per_client}")
print(f"总发送消息: {total_sent}")
print(f"总接收消息: {total_received}")
print(f"整体成功率: {overall_success_rate:.2%}")
print(f"总耗时: {total_duration:.3f}s")
print(f"消息吞吐量: {(total_sent + total_received) / total_duration:.1f} messages/s")

{
    "client_count": client_count,
    "total_sent": total_sent,
    "total_received": total_received,
    "success_rate": overall_success_rate,
    "duration": total_duration,
    "throughput": (total_sent + total_received) / total_duration,
    "client_results": results
}
"""

        execution = await self.sandbox.run_code(code, language="python")
        assert execution.error is None
        assert any("WebSocket模拟" in line for line in execution.logs.stdout)

    # ======================== 主测试执行器 ========================

    async def run_all_tests(self):
        """运行所有异步测试"""
        logger.info("开始AsyncCodeInterpreter综合验证测试...")

        # 基础异步操作测试
        await self.run_test(
            self.test_async_code_interpreter_creation, "Async CodeInterpreter Creation"
        )
        await self.run_test(
            self.test_basic_async_python_execution, "Basic Async Python Execution"
        )
        await self.run_test(
            self.test_concurrent_code_execution, "Concurrent Code Execution"
        )
        await self.run_test(
            self.test_async_data_science_workflow, "Async Data Science Workflow"
        )

        # 异步回调测试
        await self.run_test(
            self.test_async_callback_handling, "Async Callback Handling"
        )

        # 异步上下文管理测试
        await self.run_test(self.test_async_context_creation, "Async Context Creation")
        await self.run_test(
            self.test_async_context_state_management, "Async Context State Management"
        )

        # 异步性能测试
        await self.run_test(
            self.test_async_performance_concurrent_tasks,
            "Async Performance Concurrent Tasks",
        )
        await self.run_test(self.test_async_batch_processing, "Async Batch Processing")

        # 异步错误处理测试
        await self.run_test(self.test_async_error_handling, "Async Error Handling")

        # 异步结果格式测试
        await self.run_test(self.test_async_text_result, "Async Text Result Format")
        await self.run_test(
            self.test_async_mixed_format_result, "Async Mixed Format Result"
        )
        await self.run_test(
            self.test_async_realtime_data_result, "Async Realtime Data Result"
        )

        # 异步R语言测试
        await self.run_test(
            self.test_async_r_language_basic_execution,
            "Async R Language Basic Execution",
        )
        await self.run_test(
            self.test_async_r_language_data_analysis, "Async R Language Data Analysis"
        )
        await self.run_test(
            self.test_async_r_language_visualization, "Async R Language Visualization"
        )
        await self.run_test(
            self.test_async_r_language_statistics, "Async R Language Statistics"
        )
        await self.run_test(
            self.test_async_r_language_context_management,
            "Async R Language Context Management",
        )

        # 异步Node.js/JavaScript 测试
        await self.run_test(
            self.test_async_nodejs_basic_execution, "Async Node.js Basic Execution"
        )
        await self.run_test(
            self.test_async_nodejs_async_promises, "Async Node.js Async Promises"
        )
        await self.run_test(
            self.test_async_nodejs_data_processing, "Async Node.js Data Processing"
        )
        await self.run_test(
            self.test_async_nodejs_chart_data, "Async Node.js Chart Data Generation"
        )
        await self.run_test(
            self.test_async_nodejs_context_management,
            "Async Node.js Context Management",
        )

        # 异步Bash 测试
        await self.run_test(
            self.test_async_bash_basic_execution, "Async Bash Basic Execution"
        )
        await self.run_test(
            self.test_async_bash_file_operations, "Async Bash File Operations"
        )
        await self.run_test(
            self.test_async_bash_pipelines_and_grep, "Async Bash Pipelines and Grep"
        )
        await self.run_test(
            self.test_async_bash_env_and_exit_codes, "Async Bash Env and Exit Codes"
        )
        await self.run_test(
            self.test_async_bash_context_management, "Async Bash Context Management"
        )

        # 异步IJAVA 测试
        await self.run_test(
            self.test_async_ijava_basic_execution, "Async IJAVA Basic Execution"
        )
        await self.run_test(
            self.test_async_ijava_oop_features, "Async IJAVA OOP Features"
        )
        await self.run_test(
            self.test_async_ijava_collections, "Async IJAVA Collections"
        )
        await self.run_test(self.test_async_ijava_file_io, "Async IJAVA File I/O")
        await self.run_test(
            self.test_async_ijava_context_management, "Async IJAVA Context Management"
        )

        # 异步Deno 测试
        await self.run_test(
            self.test_async_deno_basic_execution, "Async Deno Basic Execution"
        )
        await self.run_test(
            self.test_async_deno_typescript_features, "Async Deno TypeScript Features"
        )
        await self.run_test(self.test_async_deno_async_await, "Async Deno Async/Await")
        await self.run_test(
            self.test_async_deno_file_operations, "Async Deno File Operations"
        )
        await self.run_test(
            self.test_async_deno_context_management, "Async Deno Context Management"
        )

        # 高级异步功能测试
        await self.run_test(
            self.test_async_websocket_simulation, "Async WebSocket Simulation"
        )

    async def cleanup(self):
        """清理资源"""
        # 清理剩余的上下文
        for name, context in self.contexts.items():
            try:
                await self.sandbox.destroy_context(context)
                logger.info(
                    f"Successfully destroyed async context {name}: {context.id}"
                )
            except Exception as e:
                logger.warning(f"Error cleaning up async context {name}: {e}")

        # 清空contexts字典
        self.contexts.clear()

        # 清理异步沙箱
        if self.sandbox:
            try:
                # await self.sandbox.kill()
                logger.info("AsyncCodeInterpreter sandbox cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up async sandbox: {e}")

    def print_summary(self):
        """打印测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        total_duration = sum(r["duration"] for r in self.test_results)

        print("\n" + "=" * 60)
        print("AsyncCodeInterpreter综合验证测试报告")
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


async def main():
    """主函数"""
    validator = AsyncCodeInterpreterValidator()

    try:
        await validator.run_all_tests()
    finally:
        await validator.cleanup()
        validator.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
