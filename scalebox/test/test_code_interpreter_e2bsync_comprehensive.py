#!/usr/bin/env python3
"""
Comprehensive validation test for code_interpreter sync module.

This test suite demonstrates and validates all key functionality of the CodeInterpreter:
- Basic code execution (Python, shell commands)
- Callback handling (stdout, stderr, result, error)
- Context management (create, persist, destroy)
- Error handling and edge cases
- Performance testing
- Different data types and formats
"""

import datetime
import logging
import os
import time
import tempfile
import json
from typing import List, Optional, Dict, Any
from io import StringIO
from e2b_code_interpreter import (
    Sandbox,
    Context,
    Execution,
    ExecutionError,
    Result,
    OutputMessage,
    Logs,
)

# from scalebox.code_interpreter import Sandbox, Context, Execution, ExecutionError, Result, OutputMessage, Logs

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CodeInterpreterValidator:
    """Comprehensive CodeInterpreter validation test suite."""

    def __init__(self):
        self.sandbox: Optional[Sandbox] = None
        self.test_results = []
        self.failed_tests = []
        self.contexts: Dict[str, Context] = {}

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

    def run_test(self, test_func, test_name: str):
        """运行单个测试并记录结果"""
        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            self.log_test_result(test_name, True, duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, str(e), duration=duration)

    # ======================== 基础代码解释器操作测试 ========================

    def test_code_interpreter_creation(self):
        """测试代码解释器创建"""
        # self.sandbox = Sandbox(
        #     template="code-interpreter",
        #     timeout=600,
        #     debug=True,
        #     metadata={"test": "code_interpreter_validation"},
        #     envs={"CI_TEST": "sync_test"}
        # )
        self.sandbox = Sandbox.create()

        # time.sleep(5)
        assert self.sandbox is not None
        assert self.sandbox.sandbox_id is not None
        logger.info(
            f"Created CodeInterpreter sandbox with ID: {self.sandbox.sandbox_id}"
        )

    def test_basic_python_execution(self):
        """测试基础Python代码执行"""
        assert self.sandbox is not None

        code = """
print("Hello, CodeInterpreter!")
x = 1 + 2
y = x * 3
print(f"计算结果: x={x}, y={y}")
result = {"x": x, "y": y}
print(result)
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert isinstance(execution, Execution)
        assert execution.error is None
        assert len(execution.logs.stdout) > 0
        assert "Hello, CodeInterpreter!" in execution.logs.stdout[0]
        logger.info(f"Python execution stdout: {execution.logs.stdout}")

    def test_math_calculations(self):
        """测试数学计算"""
        assert self.sandbox is not None

        code = """
import math
import numpy as np

# 基础数学运算
circle_radius = 5
area = math.pi * circle_radius ** 2
circumference = 2 * math.pi * circle_radius

print(f"圆的半径: {circle_radius}")
print(f"圆的面积: {area:.2f}")
print(f"圆的周长: {circumference:.2f}")

# 使用numpy进行计算
arr = np.array([1, 2, 3, 4, 5])
mean_val = np.mean(arr)
std_val = np.std(arr)

print(f"数组: {arr}")
print(f"平均值: {mean_val}")
print(f"标准差: {std_val:.3f}")

# 返回结果
{
    "circle": {"radius": circle_radius, "area": area, "circumference": circumference},
    "array_stats": {"mean": mean_val, "std": std_val}
}
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("圆的面积" in line for line in execution.logs.stdout)
        logger.info("Math calculations completed successfully")

    def test_data_processing(self):
        """测试数据处理"""
        assert self.sandbox is not None

        code = """
import pandas as pd
import json

# 创建示例数据
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [25, 30, 35, 28],
    'city': ['New York', 'London', 'Tokyo', 'Paris'],
    'salary': [50000, 75000, 80000, 65000]
}

df = pd.DataFrame(data)
print("原始数据:")
print(df)

# 数据处理
avg_age = df['age'].mean()
avg_salary = df['salary'].mean()
city_counts = df['city'].value_counts()

print(f"\\n平均年龄: {avg_age}")
print(f"平均工资: {avg_salary}")
print(f"城市分布: {city_counts.to_dict()}")

# 筛选数据
high_earners = df[df['salary'] > 60000]
print(f"\\n高收入人员:")
print(high_earners)

result = {
    "total_people": len(df),
    "avg_age": avg_age,
    "avg_salary": avg_salary,
    "high_earners": len(high_earners),
    "cities": city_counts.to_dict()
}
print(f"\\n处理结果: {json.dumps(result, indent=2)}")
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("原始数据" in line for line in execution.logs.stdout)
        assert any("平均年龄" in line for line in execution.logs.stdout)

    def test_visualization_code(self):
        """测试数据可视化代码"""
        assert self.sandbox is not None

        code = """
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

# 创建数据
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# 创建图表
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# 上子图：正弦和余弦
ax1.plot(x, y1, 'b-', label='sin(x)', linewidth=2)
ax1.plot(x, y2, 'r--', label='cos(x)', linewidth=2)
ax1.set_title('三角函数')
ax1.set_xlabel('x')
ax1.set_ylabel('y')
ax1.legend()
ax1.grid(True)

# 下子图：散点图
np.random.seed(42)
x_scatter = np.random.randn(100)
y_scatter = np.random.randn(100)
ax2.scatter(x_scatter, y_scatter, alpha=0.6, c='green')
ax2.set_title('随机散点图')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.grid(True)

plt.tight_layout()

# 保存图表为base64编码的字符串
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()
buffer.close()
plt.close()

print(f"图表已生成，大小: {len(image_base64)} 字符")
print("图表包含正弦、余弦函数和随机散点图")

# 返回结果信息
{"image_size": len(image_base64), "charts": ["sin/cos functions", "random scatter"]}
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("图表已生成" in line for line in execution.logs.stdout)

    # ======================== 回调函数测试 ========================

    def test_callback_handling(self):
        """测试回调函数处理"""
        assert self.sandbox is not None

        stdout_messages = []
        stderr_messages = []
        results = []
        errors = []

        def stdout_callback(msg: OutputMessage):
            stdout_messages.append(msg.content)
            logger.info(f"STDOUT: {msg.content}")

        def stderr_callback(msg: OutputMessage):
            stderr_messages.append(msg.content)
            logger.info(f"STDERR: {msg.content}")

        def result_callback(result: Result):
            results.append(result)
            logger.info(f"RESULT: {result}")

        def error_callback(error: ExecutionError):
            errors.append(error)
            logger.info(f"ERROR: {error.name} - {error.value}")

        code = """
import sys

print("这是标准输出消息")
print("另一条标准输出", file=sys.stdout)
print("这是标准错误消息", file=sys.stderr)

result_data = {"status": "completed", "value": 42}
print(f"最终结果: {result_data}")

result_data  # 返回结果
"""

        execution = self.sandbox.run_code(
            code,
            language="python",
            on_stdout=stdout_callback,
            on_stderr=stderr_callback,
            on_result=result_callback,
            on_error=error_callback,
        )
        print(execution.to_json())
        assert execution.error is None
        # 注意：回调可能在执行完成后才触发
        logger.info(
            f"Callback test completed. stdout: {len(stdout_messages)}, stderr: {len(stderr_messages)}"
        )

    def test_error_handling(self):
        """测试错误处理"""
        assert self.sandbox is not None

        error_messages = []

        def error_callback(error: ExecutionError):
            error_messages.append(error)
            logger.info(f"捕获错误: {error.name} - {error.value}")

        # 测试语法错误
        code_syntax_error = """
print("开始执行")
invalid syntax here  # 这里有语法错误
print("这行不会执行")
"""

        execution = self.sandbox.run_code(
            code_syntax_error, language="python", on_error=error_callback
        )
        assert execution.error is not None
        assert execution.error.name in ["SyntaxError", "ParseError"]
        logger.info(f"正确捕获语法错误: {execution.error.name}")

        # 测试运行时错误
        code_runtime_error = """
print("开始执行")
x = 10
y = 0
result = x / y  # 除零错误
print(f"结果: {result}")
"""

        execution2 = self.sandbox.run_code(
            code_runtime_error, language="python", on_error=error_callback
        )
        print(execution.to_json())
        assert execution2.error is not None
        assert "ZeroDivisionError" in execution2.error.name
        logger.info(f"正确捕获运行时错误: {execution2.error.name}")

    # ======================== 上下文管理测试 ========================

    def test_context_creation(self):
        """测试上下文创建"""
        assert self.sandbox is not None

        # 创建Python上下文
        python_context = self.sandbox.create_code_context(language="python", cwd="/tmp")
        assert isinstance(python_context, Context)
        assert python_context.id is not None
        assert python_context.language == "python"
        self.contexts["python"] = python_context
        logger.info(f"Created Python context: {python_context.id}")

        # 测试完成后立即清理context
        try:
            self.sandbox.destroy_context(python_context)
            logger.info(f"Successfully destroyed context: {python_context.id}")
            # 从contexts字典中移除
            if "python" in self.contexts:
                del self.contexts["python"]
        except Exception as e:
            logger.warning(f"Failed to destroy context {python_context.id}: {e}")

    def test_context_persistence(self):
        """测试上下文状态持久性"""
        assert self.sandbox is not None

        # 创建新的上下文用于持久性测试
        context = self.sandbox.create_code_context(language="python", cwd="/tmp")
        self.contexts["persistence_test"] = context

        # 在上下文中定义变量
        code1 = """
test_var = "Hello from context"
numbers = [1, 2, 3, 4, 5]
counter = 0
print(f"定义了变量: test_var={test_var}, numbers={numbers}")
"""

        execution1 = self.sandbox.run_code(code1, context=context)
        print(execution1.to_json())
        assert execution1.error is None

        # 在同一上下文中使用之前定义的变量
        code2 = """
print(f"从上下文读取: test_var={test_var}")
counter += 10
numbers.append(6)
print(f"修改后: counter={counter}, numbers={numbers}")
"""

        execution2 = self.sandbox.run_code(code2, context=context)
        print(execution2.to_json())
        assert execution2.error is None
        assert any("从上下文读取" in line for line in execution2.logs.stdout)
        logger.info("Context persistence test passed")

        # 测试完成后立即清理context
        try:
            self.sandbox.destroy_context(context)
            logger.info(f"Successfully destroyed persistence context: {context.id}")
            # 从contexts字典中移除
            if "persistence_test" in self.contexts:
                del self.contexts["persistence_test"]
        except Exception as e:
            logger.warning(f"Failed to destroy persistence context {context.id}: {e}")

    def test_multiple_contexts(self):
        """测试多个上下文"""
        assert self.sandbox is not None

        # 创建两个独立的上下文
        context1 = self.sandbox.create_code_context(language="python", cwd="/tmp")
        context2 = self.sandbox.create_code_context(language="python", cwd="/home")
        self.contexts["multi_context1"] = context1
        self.contexts["multi_context2"] = context2

        # 在第一个上下文中设置变量
        code1 = """
context_name = "context_1"
shared_data = {"source": "context_1", "value": 100}
print(f"在 {context_name} 中设置数据")
"""

        execution1 = self.sandbox.run_code(code1, context=context1)
        print(execution1.to_json())
        assert execution1.error is None

        # 在第二个上下文中设置不同的变量
        code2 = """
context_name = "context_2"
shared_data = {"source": "context_2", "value": 200}
print(f"在 {context_name} 中设置数据")
"""

        execution2 = self.sandbox.run_code(code2, context=context2)
        print(execution2.to_json())
        assert execution2.error is None

        # 验证两个上下文的独立性
        verify_code = """
print(f"当前上下文: {context_name}")
print(f"数据: {shared_data}")
"""

        result1 = self.sandbox.run_code(verify_code, context=context1)
        print(result1.to_json())
        result2 = self.sandbox.run_code(verify_code, context=context2)
        print(result2.to_json())
        assert result1.error is None and result2.error is None
        logger.info("Multiple contexts test passed")

        # 测试完成后立即清理所有contexts
        contexts_to_destroy = [context1, context2]
        for context in contexts_to_destroy:
            try:
                self.sandbox.destroy_context(context)
                logger.info(f"Successfully destroyed multi-context: {context.id}")
            except Exception as e:
                logger.warning(f"Failed to destroy multi-context {context.id}: {e}")

        # 从contexts字典中移除
        if "multi_context1" in self.contexts:
            del self.contexts["multi_context1"]
        if "multi_context2" in self.contexts:
            del self.contexts["multi_context2"]

    # ======================== 数据类型和格式测试 ========================

    def test_different_data_types(self):
        """测试不同数据类型"""
        assert self.sandbox is not None

        code = """
import json
import datetime
from decimal import Decimal

# 测试各种数据类型
test_data = {
    "string": "Hello, 世界!",
    "integer": 42,
    "float": 3.14159,
    "boolean": True,
    "none_value": None,
    "list": [1, 2, 3, "four", 5.0],
    "dict": {"nested": "value", "number": 123},
    "tuple": (1, 2, 3),
    "decimal": str(Decimal('123.456')),
    "datetime": datetime.datetime.now().isoformat()
}

print("数据类型测试:")
for key, value in test_data.items():
    print(f"  {key}: {value} ({type(value).__name__})")

# JSON序列化测试
json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
print(f"\\nJSON序列化长度: {len(json_str)}")

# 返回测试数据
test_data
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("数据类型测试" in line for line in execution.logs.stdout)

    def test_file_operations_simulation(self):
        """测试文件操作（模拟）"""
        assert self.sandbox is not None

        code = """
import tempfile
import os
import json

# 创建临时文件并写入数据
test_data = {
    "name": "CodeInterpreter Test",
    "timestamp": "2024-01-15 10:30:00",
    "data": [1, 2, 3, 4, 5],
    "status": "success"
}

# 写入文件
temp_file = "/tmp/ci_test_file.json"
with open(temp_file, 'w', encoding='utf-8') as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)

print(f"数据已写入文件: {temp_file}")

# 读取文件
with open(temp_file, 'r', encoding='utf-8') as f:
    loaded_data = json.load(f)

print("从文件读取的数据:")
print(json.dumps(loaded_data, ensure_ascii=False, indent=2))

# 验证数据一致性
data_match = loaded_data == test_data
print(f"\\n数据一致性检查: {data_match}")

# 文件大小
file_size = os.path.getsize(temp_file)
print(f"文件大小: {file_size} 字节")

# 清理
os.remove(temp_file)
print("临时文件已清理")

{"file_size": file_size, "data_match": data_match}
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("数据已写入文件" in line for line in execution.logs.stdout)

    # ======================== 性能测试 ========================

    def test_performance_simple_calculations(self):
        """测试简单计算性能"""
        assert self.sandbox is not None

        code = """
import time
import random

print("开始性能测试...")
start_time = time.time()

# 执行大量简单计算
total = 0
for i in range(10000):
    total += i * 2 + random.randint(1, 10)

mid_time = time.time()
calculation_time = mid_time - start_time

# 字符串操作
text_data = []
for i in range(1000):
    text_data.append(f"Item {i}: {random.choice(['A', 'B', 'C', 'D'])}")

combined_text = " | ".join(text_data)

end_time = time.time()
string_time = end_time - mid_time
total_time = end_time - start_time

print(f"计算结果: {total}")
print(f"字符串长度: {len(combined_text)}")
print(f"计算时间: {calculation_time:.3f}s")
print(f"字符串操作时间: {string_time:.3f}s")
print(f"总时间: {total_time:.3f}s")

{"total": total, "calculation_time": calculation_time, "string_time": string_time, "total_time": total_time}
"""

        start_test_time = time.time()
        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        test_duration = time.time() - start_test_time

        assert execution.error is None
        assert any("开始性能测试" in line for line in execution.logs.stdout)
        logger.info(f"Performance test completed in {test_duration:.3f}s")

        # 性能断言
        assert test_duration < 30  # 整个测试应在30秒内完成

    def test_performance_concurrent_simulation(self):
        """测试并发模拟（使用线程）"""
        assert self.sandbox is not None

        code = """
import threading
import time
import queue

results_queue = queue.Queue()

def worker_task(worker_id, iterations):
    '''模拟工作任务'''
    start_time = time.time()
    result = 0
    
    for i in range(iterations):
        result += i * worker_id
        # 模拟一些工作
        if i % 100 == 0:
            time.sleep(0.001)
    
    duration = time.time() - start_time
    results_queue.put({
        'worker_id': worker_id,
        'result': result,
        'duration': duration
    })
    return result

print("开始并发模拟测试...")
start_time = time.time()

# 创建多个线程
threads = []
num_workers = 5
iterations_per_worker = 1000

for i in range(num_workers):
    thread = threading.Thread(target=worker_task, args=(i, iterations_per_worker))
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()

end_time = time.time()
total_time = end_time - start_time

# 收集结果
results = []
while not results_queue.empty():
    results.append(results_queue.get())

print(f"\\n并发测试完成:")
print(f"工作者数量: {num_workers}")
print(f"每个工作者迭代: {iterations_per_worker}")
print(f"总执行时间: {total_time:.3f}s")

for result in results:
    print(f"工作者 {result['worker_id']}: 结果={result['result']}, 时间={result['duration']:.3f}s")

{
    "num_workers": num_workers,
    "total_time": total_time,
    "avg_worker_time": sum(r['duration'] for r in results) / len(results),
    "results": results
}
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("并发测试完成" in line for line in execution.logs.stdout)

    # ======================== 结果格式测试 ========================

    def test_text_result(self):
        """测试文本格式结果"""
        assert self.sandbox is not None

        code = """
# 生成纯文本结果
text_content = '''
这是一个多行文本结果示例
包含各种信息：
- 项目名称: CodeInterpreter
- 版本: 1.0.0
- 状态: 运行中

详细描述:
本系统能够执行Python代码并返回各种格式的结果，
支持文本、HTML、图像等多种输出格式。
'''

print("生成文本格式结果")
text_content
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert len(execution.results) > 0

        # 检查是否有文本结果
        for result in execution.results:
            if hasattr(result, "text") and result.text:
                logger.info(f"文本结果长度: {len(result.text)}")
                assert "CodeInterpreter" in result.text

    def test_html_result(self):
        """测试HTML格式结果"""
        assert self.sandbox is not None

        code = """
# 生成HTML格式结果
html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>CodeInterpreter 测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #4CAF50; color: white; padding: 15px; }
        .content { padding: 20px; }
        .status { color: #2196F3; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 CodeInterpreter 执行报告</h1>
    </div>
    <div class="content">
        <h2>执行概要</h2>
        <p class="status">状态: ✅ 成功</p>
        <p>执行时间: 2024-09-17 10:30:00</p>
        
        <h2>执行结果</h2>
        <table>
            <tr><th>指标</th><th>值</th><th>状态</th></tr>
            <tr><td>代码行数</td><td>25</td><td>✅</td></tr>
            <tr><td>执行时间</td><td>0.123s</td><td>✅</td></tr>
            <tr><td>内存使用</td><td>15.6MB</td><td>✅</td></tr>
        </table>
        
        <h2>详细信息</h2>
        <ul>
            <li>支持多种结果格式</li>
            <li>HTML渲染正常</li>
            <li>样式加载成功</li>
        </ul>
    </div>
</body>
</html>'''

print("生成HTML格式结果")
# 模拟返回HTML结果
from IPython.display import HTML
HTML(html_content)
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        logger.info("HTML格式结果测试完成")

    def test_markdown_result(self):
        """测试Markdown格式结果"""
        assert self.sandbox is not None

        code = """
# 生成Markdown格式结果
markdown_content = '''# 📊 CodeInterpreter 测试报告

## 🎯 测试概述

这是一个**CodeInterpreter**的测试报告，展示了系统的各项功能。

### ✅ 测试结果

| 测试项目 | 状态 | 执行时间 | 备注 |
|---------|------|----------|------|
| 基础执行 | ✅ 通过 | 0.123s | 正常 |
| 数据处理 | ✅ 通过 | 0.456s | 正常 |
| 图表生成 | ✅ 通过 | 0.789s | 正常 |

### 📈 性能指标

- **CPU使用率**: 15.6%
- **内存使用**: 128MB
- **执行效率**: 优秀

### 🔧 功能特性

1. **多格式支持**
   - 支持文本输出
   - 支持HTML渲染
   - 支持图像生成
   
2. **数据处理能力**
   - Pandas数据分析
   - NumPy数值计算
   - Matplotlib可视化

3. **错误处理**
   - 语法错误捕获
   - 运行时异常处理
   - 详细错误信息

### 💡 使用示例

```python
from scalebox.code_interpreter import Sandbox

# 创建沙箱
sandbox = Sandbox()

# 执行代码
result = sandbox.run_code(\"\"\"
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3]})
df.describe()
\"\"\")

print(result)
```

### 📝 总结

CodeInterpreter系统运行稳定，功能完整，性能优秀！

---

*报告生成时间: 2024-09-17 10:30:00*
'''

print("生成Markdown格式结果")
from IPython.display import Markdown
Markdown(markdown_content)
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        logger.info("Markdown格式结果测试完成")

    def test_svg_result(self):
        """测试SVG格式结果"""
        assert self.sandbox is not None

        code = """
# 生成SVG格式结果
svg_content = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <!-- 背景 -->
  <rect width="100%" height="100%" fill="#f8f9fa"/>
  
  <!-- 标题 -->
  <text x="200" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="#333">
    CodeInterpreter SVG 报告
  </text>
  
  <!-- 进度条背景 -->
  <rect x="50" y="60" width="300" height="20" fill="#e9ecef" rx="10"/>
  
  <!-- 进度条 -->
  <rect x="50" y="60" width="240" height="20" fill="#28a745" rx="10">
    <animate attributeName="width" from="0" to="240" dur="2s" repeatCount="1"/>
  </rect>
  
  <!-- 进度文本 -->
  <text x="200" y="75" text-anchor="middle" font-size="12" fill="white" font-weight="bold">
    80% 完成
  </text>
  
  <!-- 统计图表 -->
  <g transform="translate(50, 120)">
    <!-- 柱状图 -->
    <rect x="0" y="120" width="40" height="80" fill="#007bff"/>
    <rect x="60" y="100" width="40" height="100" fill="#28a745"/>
    <rect x="120" y="140" width="40" height="60" fill="#ffc107"/>
    <rect x="180" y="90" width="40" height="110" fill="#dc3545"/>
    <rect x="240" y="110" width="40" height="90" fill="#17a2b8"/>
    
    <!-- 标签 -->
    <text x="20" y="220" text-anchor="middle" font-size="10">测试A</text>
    <text x="80" y="220" text-anchor="middle" font-size="10">测试B</text>
    <text x="140" y="220" text-anchor="middle" font-size="10">测试C</text>
    <text x="200" y="220" text-anchor="middle" font-size="10">测试D</text>
    <text x="260" y="220" text-anchor="middle" font-size="10">测试E</text>
  </g>
  
  <!-- 说明文字 -->
  <text x="200" y="270" text-anchor="middle" font-size="14" fill="#666">
    各测试模块执行情况统计
  </text>
</svg>'''

print("生成SVG格式结果")
from IPython.display import SVG
SVG(svg_content)
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        logger.info("SVG格式结果测试完成")

    def test_image_results(self):
        """测试图像格式结果 (PNG/JPEG)"""
        assert self.sandbox is not None

        code = """
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

# 创建一个复杂的图表
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('CodeInterpreter 测试结果图表集', fontsize=16, fontweight='bold')

# 图表1: 正弦波
x = np.linspace(0, 4*np.pi, 100)
y1 = np.sin(x)
y2 = np.cos(x)
ax1.plot(x, y1, 'b-', label='sin(x)', linewidth=2)
ax1.plot(x, y2, 'r--', label='cos(x)', linewidth=2)
ax1.set_title('三角函数')
ax1.legend()
ax1.grid(True)

# 图表2: 柱状图
categories = ['测试A', '测试B', '测试C', '测试D', '测试E']
values = [85, 92, 78, 96, 88]
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
bars = ax2.bar(categories, values, color=colors)
ax2.set_title('测试模块得分')
ax2.set_ylabel('得分')
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{value}%', ha='center', va='bottom')

# 图表3: 饼图
labels = ['成功', '警告', '错误', '跳过']
sizes = [75, 15, 5, 5]
colors = ['#2ECC71', '#F39C12', '#E74C3C', '#95A5A6']
wedges, texts, autotexts = ax3.pie(sizes, labels=labels, colors=colors, 
                                   autopct='%1.1f%%', startangle=90)
ax3.set_title('测试结果分布')

# 图表4: 散点图
np.random.seed(42)
x_scatter = np.random.randn(100)
y_scatter = 2 * x_scatter + np.random.randn(100)
ax4.scatter(x_scatter, y_scatter, alpha=0.6, c=y_scatter, cmap='viridis')
ax4.set_title('性能相关性分析')
ax4.set_xlabel('输入复杂度')
ax4.set_ylabel('执行时间')

plt.tight_layout()

# 保存为PNG格式 (base64编码)
png_buffer = io.BytesIO()
plt.savefig(png_buffer, format='png', dpi=150, bbox_inches='tight')
png_buffer.seek(0)
png_base64 = base64.b64encode(png_buffer.getvalue()).decode()
png_buffer.close()

# 保存为JPEG格式 (base64编码)
jpeg_buffer = io.BytesIO()
plt.savefig(jpeg_buffer, format='jpeg', dpi=150, bbox_inches='tight', pil_kwargs={'quality': 95})
jpeg_buffer.seek(0)
jpeg_base64 = base64.b64encode(jpeg_buffer.getvalue()).decode()
jpeg_buffer.close()

plt.close()

print(f"生成图像结果:")
print(f"  PNG大小: {len(png_base64)} 字符")
print(f"  JPEG大小: {len(jpeg_base64)} 字符")

# 返回图像数据
{
    "png_data": png_base64,
    "jpeg_data": jpeg_base64,
    "formats": ["png", "jpeg"],
    "description": "CodeInterpreter测试结果图表集"
}
"""

        execution = self.sandbox.run_code(code, language="python")
        # for result in execution.results:
        #     print(result.__str__())
        assert execution.error is None
        assert any("生成图像结果" in line for line in execution.logs.stdout)
        logger.info("图像格式结果测试完成")

    def test_latex_result(self):
        """测试LaTeX格式结果"""
        assert self.sandbox is not None

        code = """
# 生成LaTeX格式结果
latex_content = r'''
\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{booktabs}
\\usepackage{geometry}
\\geometry{a4paper, margin=1in}

\\title{CodeInterpreter 数学公式展示}
\\author{测试系统}
\\date{\\today}

\\begin{document}

\\maketitle

\\section{基础数学公式}

\\subsection{代数公式}

二次方程求根公式:
\\begin{equation}
x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}
\\end{equation}

欧拉恒等式 (数学中最美的公式):
\\begin{equation}
e^{i\\pi} + 1 = 0
\\end{equation}

\\subsection{微积分}

导数定义:
\\begin{equation}
f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}
\\end{equation}

积分基本定理:
\\begin{equation}
\\int_a^b f(x) dx = F(b) - F(a)
\\end{equation}

\\subsection{线性代数}

矩阵乘法:
\\begin{equation}
(AB)_{ij} = \\sum_{k=1}^{n} A_{ik}B_{kj}
\\end{equation}

特征值方程:
\\begin{equation}
Av = \\lambda v
\\end{equation}

\\section{统计学公式}

正态分布概率密度函数:
\\begin{equation}
f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}
\\end{equation}

贝叶斯定理:
\\begin{equation}
P(A|B) = \\frac{P(B|A)P(A)}{P(B)}
\\end{equation}

\\section{测试数据表格}

\\begin{table}[h!]
\\centering
\\begin{tabular}{@{}lccc@{}}
\\toprule
测试模块 & 执行时间(s) & 内存使用(MB) & 状态 \\\\
\\midrule
基础运算 & 0.123 & 15.6 & ✓ \\\\
数据处理 & 0.456 & 32.1 & ✓ \\\\
图表生成 & 0.789 & 48.7 & ✓ \\\\
错误处理 & 0.234 & 12.3 & ✓ \\\\
\\bottomrule
\\end{tabular}
\\caption{CodeInterpreter性能测试结果}
\\label{tab:performance}
\\end{table}

\\section{结论}

CodeInterpreter系统能够成功处理各种数学公式和科学计算，
支持LaTeX格式输出，适用于学术和科研应用。

\\end{document}
'''

print("生成LaTeX格式结果")
from IPython.display import Latex
Latex(latex_content)
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        logger.info("LaTeX格式结果测试完成")

    def test_json_data_result(self):
        """测试JSON数据格式结果"""
        assert self.sandbox is not None

        code = """
import json
from datetime import datetime

# 生成复杂的JSON数据结构
json_data = {
    "report_info": {
        "title": "CodeInterpreter 测试报告",
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "generator": "CodeInterpreter测试系统"
    },
    "test_summary": {
        "total_tests": 25,
        "passed": 23,
        "failed": 1,
        "skipped": 1,
        "success_rate": 92.0,
        "execution_time": 45.67
    },
    "test_modules": [
        {
            "name": "基础执行",
            "tests": 8,
            "passed": 8,
            "failed": 0,
            "duration": 12.34,
            "details": {
                "memory_usage": "15.6MB",
                "cpu_time": "0.123s",
                "status": "success"
            }
        },
        {
            "name": "数据处理",
            "tests": 6,
            "passed": 5,
            "failed": 1,
            "duration": 18.92,
            "details": {
                "memory_usage": "32.1MB",
                "cpu_time": "0.456s",
                "status": "partial",
                "errors": ["数据类型不匹配"]
            }
        },
        {
            "name": "图表生成",
            "tests": 4,
            "passed": 4,
            "failed": 0,
            "duration": 8.73,
            "details": {
                "memory_usage": "48.7MB",
                "cpu_time": "0.789s",
                "status": "success",
                "formats": ["png", "svg", "pdf"]
            }
        }
    ],
    "performance_metrics": {
        "avg_response_time": 0.234,
        "max_memory_usage": 64.2,
        "cpu_utilization": 15.6,
        "disk_io": {
            "read_bytes": 1048576,
            "write_bytes": 524288
        },
        "network": {
            "requests_sent": 12,
            "requests_successful": 11,
            "bytes_transferred": 2097152
        }
    },
    "environment": {
        "python_version": "3.9.2",
        "platform": "Linux x86_64",
        "packages": {
            "numpy": "1.21.0",
            "pandas": "1.3.0",
            "matplotlib": "3.4.2"
        }
    },
    "recommendations": [
        "优化内存使用，减少峰值内存占用",
        "增加更多错误处理测试用例",
        "考虑添加异步执行支持"
    ],
    "metadata": {
        "schema_version": "2.0",
        "data_format": "json",
        "compression": "none",
        "checksum": "sha256:abc123def456"
    }
}

print("生成JSON数据格式结果")
print(f"JSON数据包含 {len(json_data)} 个顶级字段")
print(f"测试模块数量: {len(json_data['test_modules'])}")
print(f"性能指标项: {len(json_data['performance_metrics'])}")

# 格式化输出JSON
formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
print(f"\\n格式化JSON长度: {len(formatted_json)} 字符")

# 返回JSON数据
json_data
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("JSON数据格式" in line for line in execution.logs.stdout)
        logger.info("JSON数据格式结果测试完成")

    def test_javascript_result(self):
        """测试JavaScript格式结果"""
        assert self.sandbox is not None

        code = """
# 生成JavaScript格式结果
javascript_code = '''
// CodeInterpreter 交互式结果展示脚本

class CodeInterpreterResults {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = null;
        this.charts = [];
        this.init();
    }

    init() {
        console.log('CodeInterpreter Results 初始化完成');
        this.createLayout();
        this.loadTestData();
    }

    createLayout() {
        this.container.innerHTML = `
            <div class="ci-dashboard">
                <header class="ci-header">
                    <h1>🚀 CodeInterpreter 执行结果</h1>
                    <div class="ci-status" id="status">正在加载...</div>
                </header>
                
                <div class="ci-content">
                    <div class="ci-summary" id="summary"></div>
                    <div class="ci-charts" id="charts"></div>
                    <div class="ci-logs" id="logs"></div>
                </div>
            </div>
        `;
        
        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .ci-dashboard { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px; margin: 0 auto; padding: 20px;
            }
            .ci-header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
            }
            .ci-status { 
                background: rgba(255,255,255,0.2); 
                padding: 5px 15px; border-radius: 15px; 
                display: inline-block; font-size: 14px;
            }
            .ci-summary { 
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin-bottom: 20px;
            }
            .ci-card { 
                background: white; border-radius: 8px; padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
        `;
        document.head.appendChild(style);
    }

    loadTestData() {
        // 模拟加载测试数据
        this.data = {
            execution: {
                startTime: new Date().toISOString(),
                duration: 1.234,
                status: 'success',
                memory: 15.6,
                cpu: 12.3
            },
            tests: {
                total: 25,
                passed: 23,
                failed: 1,
                skipped: 1
            },
            modules: [
                {name: '基础执行', score: 95, time: 0.123},
                {name: '数据处理', score: 88, time: 0.456},
                {name: '图表生成', score: 92, time: 0.789},
                {name: '错误处理', score: 100, time: 0.234}
            ]
        };

        this.renderSummary();
        this.renderCharts();
        this.updateStatus('✅ 加载完成');
        
        // 添加交互性
        this.addInteractivity();
    }

    renderSummary() {
        const summaryEl = document.getElementById('summary');
        summaryEl.innerHTML = `
            <div class="ci-card">
                <h3>📊 执行概要</h3>
                <p>执行时间: ${this.data.execution.duration}s</p>
                <p>内存使用: ${this.data.execution.memory}MB</p>
                <p>CPU时间: ${this.data.execution.cpu}%</p>
            </div>
            <div class="ci-card">
                <h3>🎯 测试结果</h3>
                <p>总测试数: ${this.data.tests.total}</p>
                <p>通过: ${this.data.tests.passed}</p>
                <p>失败: ${this.data.tests.failed}</p>
                <p>跳过: ${this.data.tests.skipped}</p>
            </div>
            <div class="ci-card">
                <h3>⚡ 性能指标</h3>
                <p>成功率: ${Math.round(this.data.tests.passed/this.data.tests.total*100)}%</p>
                <p>平均响应: ${this.data.execution.duration/this.data.tests.total}s</p>
                <p>效率评级: A+</p>
            </div>
        `;
    }

    renderCharts() {
        const chartsEl = document.getElementById('charts');
        chartsEl.innerHTML = '<div class="ci-card"><h3>📈 性能图表</h3><canvas id="performanceChart" width="400" height="200"></canvas></div>';
        
        // 简单的canvas图表
        const canvas = document.getElementById('performanceChart');
        const ctx = canvas.getContext('2d');
        
        // 绘制柱状图
        const modules = this.data.modules;
        const barWidth = 60;
        const barSpacing = 20;
        
        modules.forEach((module, index) => {
            const x = index * (barWidth + barSpacing) + 50;
            const height = module.score * 1.5; // 缩放高度
            const y = canvas.height - height - 30;
            
            // 绘制柱子
            ctx.fillStyle = `hsl(${120 + index * 60}, 60%, 50%)`;
            ctx.fillRect(x, y, barWidth, height);
            
            // 绘制标签
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(module.name, x + barWidth/2, canvas.height - 10);
            ctx.fillText(module.score + '%', x + barWidth/2, y - 5);
        });
    }

    addInteractivity() {
        // 添加点击事件
        document.querySelectorAll('.ci-card').forEach(card => {
            card.addEventListener('click', () => {
                card.style.transform = card.style.transform ? '' : 'scale(1.02)';
            });
        });

        // 定时更新状态
        setInterval(() => {
            this.updateMemoryUsage();
        }, 2000);
    }

    updateStatus(status) {
        document.getElementById('status').textContent = status;
    }

    updateMemoryUsage() {
        // 模拟内存使用变化
        const memory = (Math.random() * 10 + 15).toFixed(1);
        const cards = document.querySelectorAll('.ci-card p');
        if (cards[1]) {
            cards[1].textContent = `内存使用: ${memory}MB`;
        }
    }

    exportResults() {
        return {
            timestamp: new Date().toISOString(),
            data: this.data,
            summary: 'CodeInterpreter执行完成',
            format: 'javascript_interactive'
        };
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('ci-results-container')) {
        const ciResults = new CodeInterpreterResults('ci-results-container');
        
        // 暴露到全局
        window.CodeInterpreterResults = ciResults;
        
        console.log('CodeInterpreter JavaScript 结果系统已启动');
    }
});
'''

print("生成JavaScript格式结果")
print(f"JavaScript代码长度: {len(javascript_code)} 字符")
print("包含完整的交互式结果展示系统")

# 模拟返回JavaScript结果
{
    "javascript_code": javascript_code,
    "type": "interactive_dashboard",
    "features": ["实时更新", "交互式图表", "响应式设计"],
    "description": "CodeInterpreter交互式结果展示系统"
}
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("JavaScript格式" in line for line in execution.logs.stdout)
        logger.info("JavaScript格式结果测试完成")

    def test_chart_data_result(self):
        """测试图表数据格式结果"""
        assert self.sandbox is not None

        code = """
import json

# 生成图表数据格式结果
chart_data = {
    "chart_type": "multi_chart_dashboard",
    "title": "CodeInterpreter 性能分析图表",
    "description": "展示各项测试指标和性能数据",
    "charts": [
        {
            "id": "performance_overview",
            "type": "line",
            "title": "性能趋势图",
            "data": {
                "labels": ["00:00", "00:15", "00:30", "00:45", "01:00"],
                "datasets": [
                    {
                        "label": "CPU使用率 (%)",
                        "data": [12, 19, 15, 25, 18],
                        "borderColor": "rgb(75, 192, 192)",
                        "tension": 0.1
                    },
                    {
                        "label": "内存使用率 (%)",
                        "data": [8, 15, 12, 20, 16],
                        "borderColor": "rgb(255, 99, 132)",
                        "tension": 0.1
                    }
                ]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {"beginAtZero": True, "max": 100}
                }
            }
        },
        {
            "id": "test_results_pie",
            "type": "pie",
            "title": "测试结果分布",
            "data": {
                "labels": ["通过", "失败", "跳过", "警告"],
                "datasets": [{
                    "data": [23, 1, 1, 2],
                    "backgroundColor": [
                        "#28a745",  # 绿色 - 通过
                        "#dc3545",  # 红色 - 失败
                        "#6c757d",  # 灰色 - 跳过
                        "#ffc107"   # 黄色 - 警告
                    ]
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "right"}
                }
            }
        },
        {
            "id": "module_scores",
            "type": "bar",
            "title": "模块测试得分",
            "data": {
                "labels": ["基础执行", "数据处理", "图表生成", "错误处理", "性能测试"],
                "datasets": [{
                    "label": "得分",
                    "data": [95, 88, 92, 100, 85],
                    "backgroundColor": [
                        "rgba(54, 162, 235, 0.8)",
                        "rgba(255, 99, 132, 0.8)",
                        "rgba(255, 205, 86, 0.8)",
                        "rgba(75, 192, 192, 0.8)",
                        "rgba(153, 102, 255, 0.8)"
                    ],
                    "borderColor": [
                        "rgba(54, 162, 235, 1)",
                        "rgba(255, 99, 132, 1)",
                        "rgba(255, 205, 86, 1)",
                        "rgba(75, 192, 192, 1)",
                        "rgba(153, 102, 255, 1)"
                    ],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {"beginAtZero": True, "max": 100}
                }
            }
        },
        {
            "id": "response_time_histogram",
            "type": "histogram",
            "title": "响应时间分布",
            "data": {
                "labels": ["0-0.1s", "0.1-0.2s", "0.2-0.5s", "0.5-1s", "1s+"],
                "datasets": [{
                    "label": "请求数量",
                    "data": [45, 32, 18, 8, 2],
                    "backgroundColor": "rgba(75, 192, 192, 0.6)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {"beginAtZero": True}
                }
            }
        }
    ],
    "summary": {
        "total_charts": 4,
        "data_points": 105,
        "time_range": "1小时",
        "update_frequency": "15秒"
    },
    "interactive_features": [
        "点击图例显示/隐藏数据系列",
        "悬停显示详细数值",
        "图表缩放和平移",
        "数据导出功能"
    ],
    "export_options": [
        "PNG图片",
        "SVG矢量图",
        "PDF报告",
        "CSV数据",
        "JSON配置"
    ],
    "metadata": {
        "created_at": "2024-09-17T10:30:00Z",
        "version": "1.0",
        "generator": "CodeInterpreter",
        "format": "chart.js_compatible"
    }
}

print("生成图表数据格式结果")
print(f"包含 {len(chart_data['charts'])} 个图表")
print(f"总数据点: {chart_data['summary']['data_points']}")

for i, chart in enumerate(chart_data['charts'], 1):
    print(f"  图表{i}: {chart['title']} ({chart['type']})")

print(f"\\n图表数据JSON长度: {len(json.dumps(chart_data))} 字符")

# 返回图表数据
chart_data
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("图表数据格式" in line for line in execution.logs.stdout)
        logger.info("图表数据格式结果测试完成")

    def test_mixed_format_result(self):
        """测试混合格式结果"""
        assert self.sandbox is not None

        code = """
import json
import base64
import matplotlib.pyplot as plt
import numpy as np
import io

# 生成混合格式的综合结果
print("生成混合格式综合结果...")

# 1. 文本摘要
text_summary = '''
CodeInterpreter 综合测试报告
================================

执行时间: 2024-09-17 10:30:00
测试模块: 17个
总体状态: ✅ 成功

主要发现:
- 所有核心功能运行正常
- 性能表现优秀
- 支持多种输出格式
- 错误处理机制完善
'''

# 2. HTML报告
html_report = '''
<div class="mixed-result-report">
    <h2>🚀 CodeInterpreter 测试完成</h2>
    <div class="status-badge success">✅ 全部通过</div>
    <ul>
        <li>文本格式: ✅</li>
        <li>HTML格式: ✅</li>
        <li>图像格式: ✅</li>
        <li>数据格式: ✅</li>
    </ul>
</div>
'''

# 3. 生成图表
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# 测试结果饼图
labels = ['通过', '失败', '警告']
sizes = [92, 4, 4]
colors = ['#28a745', '#dc3545', '#ffc107']
ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax1.set_title('测试结果分布')

# 性能趋势图
x = range(5)
performance = [85, 88, 92, 95, 93]
ax2.plot(x, performance, marker='o', linewidth=2, markersize=6)
ax2.set_title('性能趋势')
ax2.set_xlabel('测试轮次')
ax2.set_ylabel('得分')
ax2.grid(True, alpha=0.3)

plt.tight_layout()

# 转换为base64
img_buffer = io.BytesIO()
plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
img_buffer.seek(0)
img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
img_buffer.close()
plt.close()

# 4. JSON数据
json_data = {
    "test_summary": {
        "total_tests": 17,
        "passed": 16,
        "failed": 1,
        "success_rate": 94.1
    },
    "performance_metrics": {
        "execution_time": 45.67,
        "memory_peak": 64.2,
        "cpu_avg": 15.6
    },
    "module_results": [
        {"name": "基础功能", "score": 95, "status": "pass"},
        {"name": "数据处理", "score": 88, "status": "pass"},
        {"name": "图表生成", "score": 92, "status": "pass"},
        {"name": "错误处理", "score": 100, "status": "pass"}
    ]
}

# 5. LaTeX公式
latex_formula = r'''
测试成功率计算公式：
$$\\text{Success Rate} = \\frac{\\text{Passed Tests}}{\\text{Total Tests}} \\times 100\\% = \\frac{16}{17} \\times 100\\% = 94.1\\%$$
'''

# 6. Markdown格式
markdown_content = '''
## 📊 CodeInterpreter 测试总结

### ✅ 主要成就
- **高成功率**: 94.1% 的测试通过
- **多格式支持**: 支持7种不同的输出格式
- **优秀性能**: 平均响应时间 < 0.5s

### 📈 性能指标
| 指标 | 数值 | 状态 |
|------|------|------|
| 执行时间 | 45.67s | ✅ |
| 内存峰值 | 64.2MB | ✅ |
| CPU使用率 | 15.6% | ✅ |

### 🎯 下一步计划
1. 优化内存使用
2. 增加更多测试用例
3. 提升错误处理能力
'''

# 7. 生成SVG图标
svg_icon = '''
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" stroke="#28a745" stroke-width="4" fill="#d4edda"/>
  <text x="50" y="55" font-family="Arial" font-size="24" text-anchor="middle" fill="#155724">✓</text>
</svg>
'''

print(f"混合格式结果生成完成:")
print(f"  文本长度: {len(text_summary)} 字符")
print(f"  HTML长度: {len(html_report)} 字符")
print(f"  图片大小: {len(img_base64)} 字符")
print(f"  JSON字段: {len(json_data)} 个")
print(f"  LaTeX公式: 包含成功率计算")
print(f"  Markdown段落: 3个主要章节")
print(f"  SVG图标: 成功状态指示")

# 返回混合格式结果
{
    "formats": ["text", "html", "png", "json", "latex", "markdown", "svg"],
    "text": text_summary,
    "html": html_report,
    "png_data": img_base64,
    "json_data": json_data,
    "latex": latex_formula,
    "markdown": markdown_content,
    "svg": svg_icon,
    "summary": {
        "total_formats": 7,
        "content_size": len(text_summary) + len(html_report) + len(img_base64) + len(markdown_content),
        "description": "包含多种格式的综合测试结果"
    }
}
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("混合格式" in line for line in execution.logs.stdout)
        logger.info("混合格式结果测试完成")

    # ======================== R语言测试 ========================

    def test_r_language_basic_execution(self):
        """测试R语言基础执行"""
        assert self.sandbox is not None

        code = """
# R语言基础执行测试
print("Hello from R Language!")

# 基础数学运算
x <- 10
y <- 20
sum_result <- x + y
product_result <- x * y

print(paste("Sum:", sum_result))
print(paste("Product:", product_result))

# 向量操作
numbers <- c(1, 2, 3, 4, 5)
mean_value <- mean(numbers)
print(paste("Mean of numbers:", mean_value))

# 数据框创建
df <- data.frame(
  name = c("Alice", "Bob", "Charlie"),
  age = c(25, 30, 35),
  city = c("New York", "London", "Tokyo")
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

        execution = self.sandbox.run_code(code, language="r")
        print(execution.to_json())
        assert execution.error is None
        assert any("Hello from R Language!" in line for line in execution.logs.stdout)
        assert any("Sum:" in line for line in execution.logs.stdout)
        logger.info("R language basic execution test passed")

    def test_r_language_data_analysis(self):
        """测试R语言数据分析"""
        assert self.sandbox is not None

        code = """
# R语言数据分析测试
library(dplyr)

# 创建示例数据集
set.seed(123)
data <- data.frame(
  id = 1:100,
  value = rnorm(100, mean = 50, sd = 15),
  category = sample(c("A", "B", "C"), 100, replace = TRUE),
  score = runif(100, 0, 100)
)

print("Dataset created with 100 rows")
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
  filter(score > 80) %>%
  arrange(desc(score))

print(paste("High scores (>80):", nrow(high_scores), "rows"))

# 返回分析结果
list(
  total_rows = nrow(data),
  summary = summary_stats,
  grouped = grouped_stats,
  high_scores_count = nrow(high_scores)
)
"""

        execution = self.sandbox.run_code(code, language="r")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Dataset created with 100 rows" in line for line in execution.logs.stdout
        )
        assert any("Summary statistics" in line for line in execution.logs.stdout)
        logger.info("R language data analysis test passed")

    def test_r_language_visualization(self):
        """测试R语言数据可视化"""
        assert self.sandbox is not None

        code = """
# R语言数据可视化测试
library(ggplot2)

# 创建示例数据
set.seed(456)
plot_data <- data.frame(
  x = 1:50,
  y = cumsum(rnorm(50)),
  group = rep(c("Group1", "Group2"), each = 25)
)

print("Creating visualizations...")

# 基础散点图
p1 <- ggplot(plot_data, aes(x = x, y = y)) +
  geom_point() +
  geom_smooth(method = "lm") +
  labs(title = "Scatter Plot with Trend Line",
       x = "X Values", y = "Y Values") +
  theme_minimal()

print("Scatter plot created")

# 分组箱线图
p2 <- ggplot(plot_data, aes(x = group, y = y, fill = group)) +
  geom_boxplot() +
  labs(title = "Box Plot by Group",
       x = "Group", y = "Y Values") +
  theme_minimal()

print("Box plot created")

# 直方图
p3 <- ggplot(plot_data, aes(x = y)) +
  geom_histogram(bins = 20, fill = "skyblue", alpha = 0.7) +
  labs(title = "Distribution of Y Values",
       x = "Y Values", y = "Frequency") +
  theme_minimal()

print("Histogram created")

# 保存图表信息
plot_info <- list(
  scatter_plot = "Created scatter plot with trend line",
  box_plot = "Created box plot by group",
  histogram = "Created histogram of y values",
  total_plots = 3
)

print("All visualizations completed successfully")
plot_info
"""

        execution = self.sandbox.run_code(code, language="r")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Creating visualizations..." in line for line in execution.logs.stdout
        )
        assert any(
            "All visualizations completed successfully" in line
            for line in execution.logs.stdout
        )
        logger.info("R language visualization test passed")

    def test_r_language_statistics(self):
        """测试R语言统计分析"""
        assert self.sandbox is not None

        code = """
# R语言统计分析测试
library(stats)

# 创建两个样本数据
set.seed(789)
sample1 <- rnorm(100, mean = 10, sd = 2)
sample2 <- rnorm(100, mean = 12, sd = 2.5)

print("Created two sample datasets")

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

print("Descriptive statistics calculated")

# t检验
t_test_result <- t.test(sample1, sample2)
print("T-test performed")

# 相关性分析
correlation <- cor(sample1, sample2)
print(paste("Correlation coefficient:", round(correlation, 4)))

# 线性回归
lm_model <- lm(sample2 ~ sample1)
summary_lm <- summary(lm_model)
print("Linear regression model fitted")

# 正态性检验
shapiro_test1 <- shapiro.test(sample1[1:50])  # 限制样本大小
shapiro_test2 <- shapiro.test(sample2[1:50])

print("Normality tests performed")

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

        execution = self.sandbox.run_code(code, language="r")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Created two sample datasets" in line for line in execution.logs.stdout
        )
        assert any("T-test performed" in line for line in execution.logs.stdout)
        logger.info("R language statistics test passed")

    def test_r_language_context_management(self):
        """测试R语言上下文管理"""
        assert self.sandbox is not None

        # 创建R语言上下文
        r_context = self.sandbox.create_code_context(language="r", cwd="/tmp")
        self.contexts["r_language"] = r_context

        # 在上下文中定义变量和函数
        setup_code = """
# R语言上下文设置
print("Setting up R language context...")

# 定义全局变量
global_var <- "Hello from R Context"
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
  x = 1:10,
  y = (1:10) ^ 2
)

print(paste("Context setup complete. Counter:", counter))
print(paste("Cache size:", length(data_cache)))

# 返回设置信息
list(
  global_var = global_var,
  counter = counter,
  cache_size = length(data_cache),
  data_rows = nrow(sample_data)
)
"""

        execution1 = self.sandbox.run_code(setup_code, context=r_context)
        print(execution1.to_json())
        assert execution1.error is None
        assert any(
            "Setting up R language context..." in line
            for line in execution1.logs.stdout
        )

        # 在同一上下文中使用之前定义的变量和函数
        use_code = """
# 使用R语言上下文中的变量和函数
print("Using R language context...")

# 使用全局变量
print(paste("Global variable:", global_var))

# 使用函数
new_counter <- increment_counter()
print(paste("Counter after increment:", new_counter))

# 添加到缓存
cache_size <- add_to_cache("test_key", "test_value")
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

        execution2 = self.sandbox.run_code(use_code, context=r_context)
        print(execution2.to_json())
        assert execution2.error is None
        assert any(
            "Using R language context..." in line for line in execution2.logs.stdout
        )
        assert any(
            "Counter after increment:" in line for line in execution2.logs.stdout
        )
        logger.info("R language context management test passed")

        # 测试完成后立即清理context
        try:
            self.sandbox.destroy_context(r_context)
            logger.info(f"Successfully destroyed R context: {r_context.id}")
            # 从contexts字典中移除
            if "r_language" in self.contexts:
                del self.contexts["r_language"]
        except Exception as e:
            logger.warning(f"Failed to destroy R context {r_context.id}: {e}")

    # ======================== Node.js/JavaScript 测试 ========================

    def test_nodejs_basic_execution(self):
        """测试Node.js基础执行"""
        assert self.sandbox is not None

        code = """
// Node.js 基础执行测试
console.log("Hello from Node.js Kernel!");

// 基础运算与字符串模板
const a = 7;
const b = 5;
const sum = a + b;
const product = a * b;
console.log(`Sum: ${sum}`);
console.log(`Product: ${product}`);

// 对象与数组
const users = [
  { id: 1, name: "Alice", score: 88 },
  { id: 2, name: "Bob", score: 92 },
  { id: 3, name: "Charlie", score: 75 }
];
const top = users.filter(u => u.score >= 90);
console.log(`Top users: ${top.map(u => u.name).join(', ')}`);

// 返回综合数据
({ sum, product, topCount: top.length })
"""

        execution = self.sandbox.run_code(code, language="javascript")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Hello from Node.js Kernel!" in line for line in execution.logs.stdout
        )
        assert any("Sum:" in line for line in execution.logs.stdout)
        logger.info("Node.js basic execution test passed")

    def test_nodejs_async_promises(self):
        """测试Node.js异步/Promise"""
        assert self.sandbox is not None

        code = """
// Node.js 异步 Promise 测试
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  console.log("Starting async tasks...");
  const start = Date.now();
  await delay(50);
  const data = await Promise.all([
    (async () => { await delay(20); return { name: 'task1', value: 42 }; })(),
    (async () => { await delay(30); return { name: 'task2', value: 58 }; })()
  ]);
  const total = data.reduce((acc, cur) => acc + cur.value, 0);
  const duration = Date.now() - start;
  console.log(`Async tasks done in ${duration} ms`);
  return { total, duration, tasks: data.map(d => d.name) };
}

main();
"""

        execution = self.sandbox.run_code(code, language="javascript")
        print(execution.to_json())
        assert execution.error is None
        assert any("Starting async tasks..." in line for line in execution.logs.stdout)
        assert any("Async tasks done" in line for line in execution.logs.stdout)
        logger.info("Node.js async/promises test passed")

    def test_nodejs_data_processing(self):
        """测试Node.js数据处理"""
        assert self.sandbox is not None

        code = """
// Node.js 数据处理示例（无需外部库）
const records = [];
for (let i = 0; i < 100; i++) {
  records.push({ id: i + 1, value: Math.round(Math.random() * 100), group: ['A','B','C'][i % 3] });
}

const summary = records.reduce((acc, r) => {
  if (!acc[r.group]) acc[r.group] = { count: 0, sum: 0 };
  acc[r.group].count++;
  acc[r.group].sum += r.value;
  return acc;
}, {});

const grouped = Object.entries(summary).map(([group, s]) => ({ group, count: s.count, mean: s.sum / s.count }));
console.log("Grouped summary ready");
({ total: records.length, groups: grouped })
"""

        execution = self.sandbox.run_code(code, language="javascript")
        print(execution.to_json())
        assert execution.error is None
        assert any("Grouped summary ready" in line for line in execution.logs.stdout)
        logger.info("Node.js data processing test passed")

    def test_nodejs_chart_data(self):
        """测试Node.js图表数据生成（Chart.js兼容结构）"""
        assert self.sandbox is not None

        code = """
// 生成Chart.js兼容的数据对象
const labels = Array.from({length: 7}, (_, i) => `Day ${i+1}`);
const dataset = labels.map(() => Math.round(Math.random() * 100));

const chart = {
  type: 'line',
  data: {
    labels,
    datasets: [{ label: 'Random Series', data: dataset, borderColor: '#2b8a3e' }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: true } }
  }
};

console.log("Chart data generated");
({ chart })
"""

        execution = self.sandbox.run_code(code, language="javascript")
        print(execution.to_json())
        assert execution.error is None
        assert any("Chart data generated" in line for line in execution.logs.stdout)
        # 验证结果中存在chart/data之一
        assert len(execution.results) > 0
        logger.info("Node.js chart data test passed")

    def test_nodejs_context_management(self):
        """测试Node.js上下文管理"""
        assert self.sandbox is not None

        # 创建Node.js上下文
        js_context = self.sandbox.create_code_context(language="javascript", cwd="/tmp")
        self.contexts["nodejs"] = js_context

        # 在上下文中定义变量与函数
        setup = """
// Node.js 上下文初始化
console.log("Setting up Node.js context...");
globalThis.cache = { items: [] };
function addItem(x) { globalThis.cache.items.push(x); return globalThis.cache.items.length; }
function sum(a,b) { return a + b; }
console.log(`Init done with ${globalThis.cache.items.length} items`);
({ size: globalThis.cache.items.length })
"""

        exec1 = self.sandbox.run_code(setup, context=js_context)
        print(exec1.to_json())
        assert exec1.error is None
        assert any(
            "Setting up Node.js context..." in line for line in exec1.logs.stdout
        )

        # 使用上下文中的函数与状态
        use = """
console.log("Using Node.js context...");
const n1 = addItem({ id: 1, value: 10 });
const n2 = addItem({ id: 2, value: 15 });
const s = sum(3, 4);
console.log(`Items now: ${n2}, sum=${s}`);
({ items: n2, sum: s })
"""

        exec2 = self.sandbox.run_code(use, context=js_context)
        print(exec2.to_json())
        assert exec2.error is None
        assert any("Using Node.js context..." in line for line in exec2.logs.stdout)

        # 清理上下文
        try:
            self.sandbox.destroy_context(js_context)
            if "nodejs" in self.contexts:
                del self.contexts["nodejs"]
            logger.info("Destroyed Node.js context")
        except Exception as e:
            logger.warning(f"Failed to destroy Node.js context: {e}")

    # ======================== Bash 测试 ========================

    def test_bash_basic_execution(self):
        """测试Bash基础执行"""
        assert self.sandbox is not None

        code = """
# Bash 基础执行
echo "Hello from Bash Kernel!"
NAME="scalebox"
GREETING="Hello, ${NAME}!"
echo "${GREETING}"
echo "Current user: $(whoami)"
date
"""

        execution = self.sandbox.run_code(code, language="bash")
        print(execution.to_json())
        assert execution.error is None
        assert any("Hello from Bash Kernel!" in line for line in execution.logs.stdout)
        assert any("Hello, scalebox!" in line for line in execution.logs.stdout)
        logger.info("Bash basic execution test passed")

    def test_bash_file_operations(self):
        """测试Bash文件操作"""
        assert self.sandbox is not None

        code = """
set -e
echo "Creating files..."
WORKDIR="/tmp/bash_demo"
mkdir -p "$WORKDIR"
cd "$WORKDIR"
echo "alpha" > a.txt
echo "beta" > b.txt
cat a.txt b.txt > all.txt
echo "Files in $(pwd):"
ls -l
wc -l all.txt
echo "Done"
"""

        execution = self.sandbox.run_code(code, language="bash")
        print(execution.to_json())
        assert execution.error is None
        assert any("Creating files..." in line for line in execution.logs.stdout)
        assert any("Done" in line for line in execution.logs.stdout)
        logger.info("Bash file operations test passed")

    def test_bash_pipelines_and_grep(self):
        """测试Bash管道与grep"""
        assert self.sandbox is not None

        code = """
set -e
printf "%s\n" foo bar baz foo bar | grep -n "foo" | awk -F: '{print "line", $1, ":", $2}'
echo "PIPELINE_OK"
"""

        execution = self.sandbox.run_code(code, language="bash")
        print(execution.to_json())
        assert execution.error is None
        assert any("PIPELINE_OK" in line for line in execution.logs.stdout)
        logger.info("Bash pipelines/grep test passed")

    def test_bash_env_and_exit_codes(self):
        """测试Bash环境变量与退出码"""
        assert self.sandbox is not None

        code = """
export APP_ENV=production
echo "ENV=$APP_ENV"
(exit 7)
echo $?
"""

        execution = self.sandbox.run_code(code, language="bash")
        print(execution.to_json())
        assert execution.error is None
        assert any("ENV=production" in line for line in execution.logs.stdout)
        # 由于shell分行执行，上一条(exit 7)的退出码会在下一行$?中打印为7
        assert any(line.strip() == "7" for line in execution.logs.stdout)
        logger.info("Bash env and exit codes test passed")

    def test_bash_context_management(self):
        """测试Bash上下文管理"""
        assert self.sandbox is not None

        # 创建Bash上下文
        bash_ctx = self.sandbox.create_code_context(language="bash", cwd="/tmp")
        self.contexts["bash"] = bash_ctx

        setup = """
echo "Setting up Bash context..."
MYVAR=42
echo $MYVAR
"""

        e1 = self.sandbox.run_code(setup, context=bash_ctx)
        print(e1.to_json())
        assert e1.error is None
        assert any("Setting up Bash context..." in line for line in e1.logs.stdout)

        use = """
echo "Using Bash context..."
echo "MYVAR=$MYVAR"
MYVAR=$((MYVAR+8))
echo "MYVAR_AFTER=$MYVAR"
"""

        e2 = self.sandbox.run_code(use, context=bash_ctx)
        print(e2.to_json())
        assert e2.error is None
        assert any("Using Bash context..." in line for line in e2.logs.stdout)
        assert any("MYVAR_AFTER=50" in line for line in e2.logs.stdout)

        # 清理上下文
        try:
            self.sandbox.destroy_context(bash_ctx)
            if "bash" in self.contexts:
                del self.contexts["bash"]
            logger.info("Destroyed Bash context")
        except Exception as e:
            logger.warning(f"Failed to destroy Bash context: {e}")

    # ======================== IJAVA 测试 ========================

    def test_ijava_basic_execution(self):
        """测试IJAVA基础执行"""
        assert self.sandbox is not None

        code = """
// IJAVA 基础执行测试
System.out.println("Hello from IJAVA Kernel!");

// 基础变量和运算
int a = 10;
int b = 20;
int sum = a + b;
int product = a * b;

System.out.println("Sum: " + sum);
System.out.println("Product: " + product);

// 字符串操作
String name = "ScaleBox";
String greeting = "Hello, " + name + "!";
System.out.println(greeting);

// 数组操作
int[] numbers = {1, 2, 3, 4, 5};
int total = 0;
for (int num : numbers) {
    total += num;
}
System.out.println("Array sum: " + total);

// 正确输出变量
System.out.println(a);
System.out.println(b);
System.out.println(sum);
"""

        execution = self.sandbox.run_code(code, language="java")
        print(execution.to_json())
        assert execution.error is None
        assert any("Hello from IJAVA Kernel!" in line for line in execution.logs.stdout)
        assert any("Sum: 30" in line for line in execution.logs.stdout)
        assert any("Array sum: 15" in line for line in execution.logs.stdout)
        logger.info("IJAVA basic execution test passed")

    def test_ijava_oop_features(self):
        """测试IJAVA面向对象特性"""
        assert self.sandbox is not None

        code = """
// IJAVA 面向对象特性测试
System.out.println("Testing IJAVA OOP features...");

// 定义类
class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() { return name; }
    public int getAge() { return age; }
    
    public void introduce() {
        System.out.println("Hi, I'm " + name + " and I'm " + age + " years old.");
    }
}

class Student extends Person {
    private String major;
    
    public Student(String name, int age, String major) {
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
Person person = new Person("Alice", 25);
person.introduce();

Student student = new Student("Bob", 22, "Computer Science");
student.introduce();

// IJAVA 特色：直接输出对象信息
person.getName();
student.getAge();
student;

System.out.println("IJAVA OOP test completed successfully!");
"""

        execution = self.sandbox.run_code(code, language="java")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Testing IJAVA OOP features..." in line for line in execution.logs.stdout
        )
        assert any("Hi, I'm Alice" in line for line in execution.logs.stdout)
        assert any(
            "I'm studying Computer Science" in line for line in execution.logs.stdout
        )
        logger.info("IJAVA OOP features test passed")

    def test_ijava_collections(self):
        """测试IJAVA集合框架"""
        assert self.sandbox is not None

        code = """
import java.util.*;

System.out.println("Testing IJAVA Collections...");

// ArrayList
List<String> fruits = new ArrayList<>();
fruits.add("Apple");
fruits.add("Banana");
fruits.add("Orange");
System.out.println("Fruits: " + fruits);

// HashMap
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 95);
scores.put("Bob", 87);
scores.put("Charlie", 92);
System.out.println("Scores: " + scores);

// HashSet
Set<Integer> numbers = new HashSet<>();
numbers.add(1);
numbers.add(2);
numbers.add(3);
numbers.add(2); // 重复元素
System.out.println("Unique numbers: " + numbers);

// 遍历集合
System.out.println("Iterating through fruits:");
for (String fruit : fruits) {
    System.out.println("- " + fruit);
}

// IJAVA 特色：直接输出集合内容
fruits;
scores;
numbers;

// 集合操作
fruits.size();
scores.containsKey("Alice");
numbers.contains(2);

System.out.println("IJAVA Collections test completed!");
"""

        execution = self.sandbox.run_code(code, language="java")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Testing IJAVA Collections..." in line for line in execution.logs.stdout
        )
        assert any(
            "Fruits: [Apple, Banana, Orange]" in line for line in execution.logs.stdout
        )
        assert any(
            "Unique numbers: [1, 2, 3]" in line for line in execution.logs.stdout
        )
        logger.info("IJAVA collections test passed")

    def test_ijava_file_io(self):
        """测试IJAVA文件I/O"""
        assert self.sandbox is not None

        code = """
import java.io.*;
import java.nio.file.*;
import java.util.*;

System.out.println("Testing IJAVA File I/O...");

try {
    // 创建临时目录
    Path tempDir = Files.createTempDirectory("ijava_demo");
    System.out.println("Created temp directory: " + tempDir);

    // 用 List 拼装多行内容（避免跨行字面量）
    List<String> lines = Arrays.asList(
        "Hello from IJAVA File I/O!",
        "This is a test file."
    );
    Path filePath = tempDir.resolve("test.txt");
    Files.write(filePath, lines);   // 直接写行列表
    System.out.println("File written successfully");

    // 读取文件
    List<String> readLines = Files.readAllLines(filePath);
    System.out.println("File content:");
    readLines.forEach(System.out::println);

    // 文件信息
    long size = Files.size(filePath);
    System.out.println("File size: " + size + " bytes");

    // 输出变量（改成打印语句）
    System.out.println("filePath = " + filePath);
    System.out.println("size = " + size);
    System.out.println("exists = " + Files.exists(filePath));

    // 清理
    Files.delete(filePath);
    Files.delete(tempDir);
    System.out.println("IJAVA File I/O test completed successfully!");

} catch (IOException e) {
    System.err.println("Error: " + e.getMessage());
}
"""

        execution = self.sandbox.run_code(code, language="java")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Testing IJAVA File I/O..." in line for line in execution.logs.stdout
        )
        assert any(
            "File written successfully" in line for line in execution.logs.stdout
        )
        assert any(
            "Hello from IJAVA File I/O!" in line for line in execution.logs.stdout
        )
        logger.info("IJAVA file I/O test passed")

    def test_ijava_context_management(self):
        """测试IJAVA上下文管理"""
        assert self.sandbox is not None

        # 创建IJAVA上下文
        ijava_context = self.sandbox.create_code_context(language="java", cwd="/tmp")
        self.contexts["ijava"] = ijava_context

        # 在上下文中定义类和变量
        setup_code = """
System.out.println("Setting up IJAVA context...");

// 定义全局变量
int counter = 0;
String message = "Hello from IJAVA Context!";

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
class ContextDemo {
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

        execution1 = self.sandbox.run_code(setup_code, context=ijava_context)
        print(execution1.to_json())
        assert execution1.error is None
        assert any(
            "Setting up IJAVA context..." in line for line in execution1.logs.stdout
        )
        assert any("Initial counter: 0" in line for line in execution1.logs.stdout)

        # 在同一上下文中使用之前定义的变量和方法
        use_code = """
System.out.println("Using IJAVA context...");

// 使用之前定义的变量和方法
incrementCounter();
int currentCounter = getCounter();
System.out.println("Current counter: " + currentCounter);

// 使用之前定义的类
ContextDemo.incrementStaticCounter();
int staticCounter = ContextDemo.getStaticCounter();
System.out.println("Static counter: " + staticCounter);

// 创建新变量
String newMessage = "Modified context data";
System.out.println("New message: " + newMessage);

// IJAVA 特色：直接输出所有变量
counter;
currentCounter;
staticCounter;
newMessage;
ContextDemo.getStaticCounter();

System.out.println("IJAVA context usage completed!");
"""

        execution2 = self.sandbox.run_code(use_code, context=ijava_context)
        print(execution2.to_json())
        assert execution2.error is None
        assert any("Using IJAVA context..." in line for line in execution2.logs.stdout)
        assert any("Current counter: 2" in line for line in execution2.logs.stdout)
        assert any("Static counter: 1" in line for line in execution2.logs.stdout)
        logger.info("IJAVA context management test passed")

        # 测试完成后立即清理context
        try:
            self.sandbox.destroy_context(ijava_context)
            logger.info(f"Successfully destroyed IJAVA context: {ijava_context.id}")
            # 从contexts字典中移除
            if "ijava" in self.contexts:
                del self.contexts["ijava"]
        except Exception as e:
            logger.warning(f"Failed to destroy IJAVA context {ijava_context.id}: {e}")

    # ======================== Deno 测试 ========================

    def test_deno_basic_execution(self):
        """测试Deno基础执行"""
        assert self.sandbox is not None

        code = """
// Deno 基础执行测试
console.log("Hello from Deno Kernel!");

// 基础变量和运算
const a: number = 12;
const b: number = 18;
const sum: number = a + b;
const product: number = a * b;

console.log(`Sum: ${sum}`);
console.log(`Product: ${product}`);

// 字符串操作
const name: string = "DenoScaleBox";
const greeting: string = `Hello, ${name}!`;
console.log(greeting);

// 数组操作
const numbers: number[] = [1, 2, 3, 4, 5];
const total: number = numbers.reduce((acc, num) => acc + num, 0);
console.log(`Array sum: ${total}`);

// 对象操作
const person = {
  name: "Alice",
  age: 25,
  city: "Tokyo"
};
console.log(`Person: ${person.name}, ${person.age} years old`);
"""

        execution = self.sandbox.run_code(code, language="typescript")
        print(execution.to_json())
        assert execution.error is None
        assert any("Hello from Deno Kernel!" in line for line in execution.logs.stdout)
        assert any("Sum: 30" in line for line in execution.logs.stdout)
        assert any("Array sum: 15" in line for line in execution.logs.stdout)
        logger.info("Deno basic execution test passed")

    def test_deno_typescript_features(self):
        """测试Deno TypeScript特性"""
        assert self.sandbox is not None

        code = """
// Deno TypeScript 特性测试
interface User {
  id: number;
  name: string;
  email: string;
  isActive: boolean;
}

class UserManager {
  private users: User[] = [];
  
  constructor() {
    console.log("UserManager initialized");
  }
  
  addUser(user: User): void {
    this.users.push(user);
    console.log(`Added user: ${user.name}`);
  }
  
  getUsers(): User[] {
    return this.users;
  }
  
  findUserById(id: number): User | undefined {
    return this.users.find(user => user.id === id);
  }
}

// 使用泛型
function processItems<T>(items: T[], processor: (item: T) => void): void {
  items.forEach(processor);
}

// 枚举
enum Status {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected"
}

console.log("Testing Deno TypeScript features...");

const userManager = new UserManager();
userManager.addUser({
  id: 1,
  name: "John Doe",
  email: "john@example.com",
  isActive: true
});

userManager.addUser({
  id: 2,
  name: "Jane Smith",
  email: "jane@example.com",
  isActive: false
});

const users = userManager.getUsers();
console.log(`Total users: ${users.length}`);

const foundUser = userManager.findUserById(1);
console.log(`Found user: ${foundUser?.name}`);

// 使用泛型函数
const numbers = [1, 2, 3, 4, 5];
processItems(numbers, (num) => console.log(`Processing: ${num}`));

console.log(`Status: ${Status.APPROVED}`);
console.log("TypeScript features test completed!");
"""

        execution = self.sandbox.run_code(code, language="typescript")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Testing Deno TypeScript features..." in line
            for line in execution.logs.stdout
        )
        assert any("Added user: John Doe" in line for line in execution.logs.stdout)
        assert any("Total users: 2" in line for line in execution.logs.stdout)
        logger.info("Deno TypeScript features test passed")

    def test_deno_async_await(self):
        """测试Deno异步/await"""
        assert self.sandbox is not None

        code = """
// Deno 异步/await 测试
async function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchData(id: number): Promise<{ id: number; data: string }> {
  await delay(50);
  return { id, data: `Data for ID ${id}` };
}

async function processBatch(ids: number[]): Promise<string[]> {
  console.log("Starting batch processing...");
  const start = Date.now();

  const results = await Promise.all(
    ids.map(async (id) => {
      const result = await fetchData(id);
      console.log(`Processed: ${result.data}`);
      return result.data;
    })
  );

  const duration = Date.now() - start;
  console.log(`Batch processing completed in ${duration}ms`);
  return results;
}

async function main(): Promise<void> {
  console.log("Testing Deno async/await...");
  const ids = [1, 2, 3, 4, 5];
  const results = await processBatch(ids);
  console.log(`Total results: ${results.length}`);
  console.log("Async/await test completed!");
}

// 顶层 await，让内核等待完成
await main();
"""

        execution = self.sandbox.run_code(code, language="typescript")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Testing Deno async/await..." in line for line in execution.logs.stdout
        )
        assert any(
            "Starting batch processing..." in line for line in execution.logs.stdout
        )
        assert any(
            "Batch processing completed" in line for line in execution.logs.stdout
        )
        logger.info("Deno async/await test passed")

    def test_deno_file_operations(self):
        """测试Deno文件操作"""
        assert self.sandbox is not None

        code = """
// Deno 文件操作测试（原生 API，兼容 1.x+）
await (async () => {
  console.log("Testing Deno file operations...");

  try {
    const tempDir = "/tmp/deno_demo";
    await Deno.mkdir(tempDir, { recursive: true });
    console.log(`Created directory: ${tempDir}`);

    const filePath = `${tempDir}/test.txt`;
    const content = "Hello from Deno File Operations!This is a test file.";
    await Deno.writeTextFile(filePath, content);
    console.log("File written successfully");

    const readContent = await Deno.readTextFile(filePath);
    console.log("File content:");
    console.log(readContent);

    const { size } = await Deno.stat(filePath);
    console.log(`File size: ${size} bytes`);

    await Deno.remove(tempDir, { recursive: true });
    console.log("File operations test completed successfully!");
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
})();
"""

        execution = self.sandbox.run_code(code, language="typescript")
        print(execution.to_json())
        assert execution.error is None
        assert any(
            "Testing Deno file operations..." in line for line in execution.logs.stdout
        )
        assert any(
            "File written successfully" in line for line in execution.logs.stdout
        )
        assert any(
            "Hello from Deno File Operations!" in line for line in execution.logs.stdout
        )
        logger.info("Deno file operations test passed")

    def test_deno_context_management(self):
        """测试Deno上下文管理"""
        assert self.sandbox is not None

        # 创建Deno上下文
        deno_context = self.sandbox.create_code_context(
            language="typescript", cwd="/tmp"
        )
        self.contexts["deno"] = deno_context

        # 在上下文中定义变量和函数
        setup_code = """
// Deno 上下文设置
console.log("Setting up Deno context...");

// 定义全局变量
let counter: number = 0;
const cache: Map<string, any> = new Map();

// 定义函数
function incrementCounter(): number {
  counter++;
  return counter;
}

function addToCache(key: string, value: any): number {
  cache.set(key, value);
  return cache.size;
}

// 定义接口
interface ContextData {
  id: number;
  value: string;
}

const contextData: ContextData = {
  id: 1,
  value: "Hello from Deno Context!"
};

console.log(`Initial counter: ${counter}`);
console.log(`Cache size: ${cache.size}`);
console.log(`Context data: ${contextData.value}`);
"""

        execution1 = self.sandbox.run_code(setup_code, context=deno_context)
        print(execution1.to_json())
        assert execution1.error is None
        assert any(
            "Setting up Deno context..." in line for line in execution1.logs.stdout
        )
        assert any("Initial counter: 0" in line for line in execution1.logs.stdout)

        # 在同一上下文中使用之前定义的变量和函数
        use_code = """
// 使用 Deno 上下文中的变量和函数
console.log("Using Deno context...");

// 使用全局变量
console.log(`Current counter: ${counter}`);
console.log(`Current cache size: ${cache.size}`);

// 使用函数
const newCounter = incrementCounter();
console.log(`Counter after increment: ${newCounter}`);

const newCacheSize = addToCache("test_key", "test_value");
console.log(`Cache size after addition: ${newCacheSize}`);

// 使用上下文数据
console.log(`Context data ID: ${contextData.id}`);
console.log(`Context data value: ${contextData.value}`);

// 修改上下文数据
contextData.value = "Modified context data";
console.log(`Modified context data: ${contextData.value}`);

console.log("Context usage completed!");
"""

        execution2 = self.sandbox.run_code(use_code, context=deno_context)
        print(execution2.to_json())
        assert execution2.error is None
        assert any("Using Deno context..." in line for line in execution2.logs.stdout)
        assert any(
            "Counter after increment: 1" in line for line in execution2.logs.stdout
        )
        assert any(
            "Cache size after addition: 1" in line for line in execution2.logs.stdout
        )
        logger.info("Deno context management test passed")

        # 测试完成后立即清理context
        try:
            self.sandbox.destroy_context(deno_context)
            logger.info(f"Successfully destroyed Deno context: {deno_context.id}")
            # 从contexts字典中移除
            if "deno" in self.contexts:
                del self.contexts["deno"]
        except Exception as e:
            logger.warning(f"Failed to destroy Deno context {deno_context.id}: {e}")

    # ======================== 高级功能测试 ========================

    def test_web_request_simulation(self):
        """测试网络请求模拟"""
        assert self.sandbox is not None

        code = """
import json
import time
from datetime import datetime

def simulate_api_call(url, method="GET", data=None):
    '''模拟API调用'''
    # 模拟网络延迟
    time.sleep(0.1)
    
    # 根据URL返回不同的模拟数据
    if "users" in url:
        return {
            "status_code": 200,
            "data": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ],
            "timestamp": datetime.now().isoformat()
        }
    elif "weather" in url:
        return {
            "status_code": 200,
            "data": {
                "location": "Beijing",
                "temperature": 22,
                "humidity": 65,
                "description": "晴朗"
            },
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status_code": 404,
            "error": "Not Found",
            "timestamp": datetime.now().isoformat()
        }

print("开始API调用模拟...")

# 模拟多个API调用
apis = [
    "https://api.example.com/users",
    "https://api.example.com/weather",
    "https://api.example.com/unknown"
]

results = []
for api_url in apis:
    print(f"\\n调用 {api_url}")
    response = simulate_api_call(api_url)
    results.append({
        "url": api_url,
        "status": response["status_code"],
        "response": response
    })
    print(f"状态码: {response['status_code']}")
    if response["status_code"] == 200:
        print(f"数据: {json.dumps(response['data'], ensure_ascii=False, indent=2)}")

print(f"\\n完成 {len(results)} 个API调用")

{
    "total_calls": len(results),
    "successful_calls": sum(1 for r in results if r["status"] == 200),
    "results": results
}
"""

        execution = self.sandbox.run_code(code, language="python")
        print(execution.to_json())
        assert execution.error is None
        assert any("API调用模拟" in line for line in execution.logs.stdout)

    # ======================== 主测试执行器 ========================

    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始CodeInterpreter综合验证测试...")

        # 基础操作测试
        self.run_test(self.test_code_interpreter_creation, "CodeInterpreter Creation")
        self.run_test(self.test_basic_python_execution, "Basic Python Execution")
        self.run_test(self.test_math_calculations, "Math Calculations")
        self.run_test(self.test_data_processing, "Data Processing")
        self.run_test(self.test_visualization_code, "Visualization Code")

        # 回调函数测试
        self.run_test(self.test_callback_handling, "Callback Handling")
        self.run_test(self.test_error_handling, "Error Handling")

        # 上下文管理测试
        self.run_test(self.test_context_creation, "Context Creation")
        self.run_test(self.test_context_persistence, "Context Persistence")
        self.run_test(self.test_multiple_contexts, "Multiple Contexts")

        # 数据类型测试
        self.run_test(self.test_different_data_types, "Different Data Types")
        self.run_test(
            self.test_file_operations_simulation, "File Operations Simulation"
        )

        # 性能测试
        self.run_test(
            self.test_performance_simple_calculations, "Performance Simple Calculations"
        )
        self.run_test(
            self.test_performance_concurrent_simulation,
            "Performance Concurrent Simulation",
        )

        # 结果格式测试
        self.run_test(self.test_text_result, "Text Result Format")
        self.run_test(self.test_html_result, "HTML Result Format")
        self.run_test(self.test_markdown_result, "Markdown Result Format")
        self.run_test(self.test_svg_result, "SVG Result Format")
        self.run_test(self.test_image_results, "Image Result Formats (PNG/JPEG)")
        self.run_test(self.test_latex_result, "LaTeX Result Format")
        self.run_test(self.test_json_data_result, "JSON Data Result Format")
        self.run_test(self.test_javascript_result, "JavaScript Result Format")
        self.run_test(self.test_chart_data_result, "Chart Data Result Format")
        self.run_test(self.test_mixed_format_result, "Mixed Format Result")

        # R语言测试
        self.run_test(
            self.test_r_language_basic_execution, "R Language Basic Execution"
        )
        self.run_test(self.test_r_language_data_analysis, "R Language Data Analysis")
        self.run_test(self.test_r_language_visualization, "R Language Visualization")
        self.run_test(self.test_r_language_statistics, "R Language Statistics")
        self.run_test(
            self.test_r_language_context_management, "R Language Context Management"
        )

        # Node.js/JavaScript 测试
        self.run_test(self.test_nodejs_basic_execution, "Node.js Basic Execution")
        self.run_test(self.test_nodejs_async_promises, "Node.js Async Promises")
        self.run_test(self.test_nodejs_data_processing, "Node.js Data Processing")
        self.run_test(self.test_nodejs_chart_data, "Node.js Chart Data Generation")
        self.run_test(self.test_nodejs_context_management, "Node.js Context Management")

        # Bash 测试
        self.run_test(self.test_bash_basic_execution, "Bash Basic Execution")
        self.run_test(self.test_bash_file_operations, "Bash File Operations")
        self.run_test(self.test_bash_pipelines_and_grep, "Bash Pipelines and Grep")
        # self.run_test(self.test_bash_env_and_exit_codes, "Bash Env and Exit Codes")
        self.run_test(self.test_bash_context_management, "Bash Context Management")

        # IJAVA 测试
        self.run_test(self.test_ijava_basic_execution, "IJAVA Basic Execution")
        self.run_test(self.test_ijava_oop_features, "IJAVA OOP Features")
        self.run_test(self.test_ijava_collections, "IJAVA Collections")
        self.run_test(self.test_ijava_file_io, "IJAVA File I/O")
        self.run_test(self.test_ijava_context_management, "IJAVA Context Management")

        # Deno 测试
        self.run_test(self.test_deno_basic_execution, "Deno Basic Execution")
        self.run_test(self.test_deno_typescript_features, "Deno TypeScript Features")
        self.run_test(self.test_deno_async_await, "Deno Async/Await")
        self.run_test(self.test_deno_file_operations, "Deno File Operations")
        self.run_test(self.test_deno_context_management, "Deno Context Management")

        # 高级功能测试
        self.run_test(self.test_web_request_simulation, "Web Request Simulation")

    def cleanup(self):
        """清理资源"""
        # 清理剩余的上下文
        for name, context in self.contexts.items():
            try:
                self.sandbox.destroy_context(context)
                logger.info(f"Successfully destroyed context {name}: {context.id}")
            except Exception as e:
                logger.warning(f"Error cleaning up context {name}: {e}")

        # 清空contexts字典
        self.contexts.clear()

        # 清理沙箱
        if self.sandbox:
            try:
                self.sandbox.kill()
                logger.info("CodeInterpreter sandbox cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up sandbox: {e}")

    def print_summary(self):
        """打印测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        total_duration = sum(r["duration"] for r in self.test_results)

        print("\n" + "=" * 60)
        print("CodeInterpreter综合验证测试报告")
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


def main():
    """主函数"""
    validator = CodeInterpreterValidator()

    try:
        validator.run_all_tests()
    finally:
        validator.cleanup()
        validator.print_summary()


if __name__ == "__main__":
    main()
