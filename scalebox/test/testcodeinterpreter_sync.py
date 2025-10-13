#!/usr/bin/env python3
"""
Simple sync CodeInterpreter test example.
Similar to testsandbox_sync.py but for code interpreter functionality.
"""

from scalebox.code_interpreter import Context, Sandbox


def output_handler(output):
    """处理输出的回调函数"""
    print(f"输出: {output.content}")


def result_handler(result):
    """处理结果的回调函数"""
    print(f"结果: {result}")


def error_handler(error):
    """处理错误的回调函数"""
    print(f"错误: {error.name} - {error.value}")


# 创建代码解释器沙箱
sandbox = Sandbox(template="code-interpreter-v1")

print("=== 基础Python代码执行 ===")
# 基础Python代码执行
result = sandbox.run_code(
    """
print("Hello from CodeInterpreter!")
x = 1 + 2
y = x * 3
print(f"计算结果: x={x}, y={y}")
{"x": x, "y": y}
""",
    language="python",
)

print(f"执行结果: {result}")
print(f"标准输出: {result.logs.stdout}")
if result.error:
    print(f"错误: {result.error}")

print("\n=== 数学计算示例 ===")
# 数学计算
math_result = sandbox.run_code(
    """
import math
import numpy as np

# 计算圆的面积和周长
radius = 5
area = math.pi * radius ** 2
circumference = 2 * math.pi * radius

print(f"半径: {radius}")
print(f"面积: {area:.2f}")
print(f"周长: {circumference:.2f}")

# 使用numpy
arr = np.array([1, 2, 3, 4, 5])
mean_val = np.mean(arr)
print(f"数组平均值: {mean_val}")

{"radius": radius, "area": area, "mean": mean_val}
"""
)

print(f"数学计算结果: {math_result}")

print("\n=== 使用回调函数 ===")
# 使用回调函数
callback_result = sandbox.run_code(
    """
print("开始执行带回调的代码")
for i in range(3):
    print(f"步骤 {i+1}")

result_data = {"steps": 3, "status": "completed"}
print(f"执行完成: {result_data}")
result_data
""",
    on_stdout=output_handler,
    on_result=result_handler,
    on_error=error_handler,
)

print("\n=== 创建和使用上下文 ===")
# 创建上下文
context = sandbox.create_code_context(language="python", cwd="/tmp")
print(f"创建上下文: {context.id}")

# 在上下文中执行代码
context_result1 = sandbox.run_code(
    """
# 在上下文中定义变量
context_var = "Hello from context"
numbers = [1, 2, 3, 4, 5]
print(f"定义了变量: {context_var}")
print(f"数组: {numbers}")
""",
    context=context,
)

# 在同一上下文中使用变量
context_result2 = sandbox.run_code(
    """
print(f"从上下文读取: {context_var}")
numbers.append(6)
print(f"修改后的数组: {numbers}")
sum(numbers)
""",
    context=context,
)

print(f"上下文测试结果: {context_result2}")

print("\n=== 错误处理示例 ===")
# 故意产生错误
error_result = sandbox.run_code(
    """
print("这行会执行")
x = 10 / 0  # 这里会产生除零错误
print("这行不会执行")
""",
    on_error=error_handler,
)

print(f"错误处理结果: {error_result.error}")

print("\n=== 数据处理示例 ===")
# 数据处理
data_result = sandbox.run_code(
    """
import pandas as pd

# 创建示例数据
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'London', 'Tokyo']
}

df = pd.DataFrame(data)
print("数据框:")
print(df)

# 简单分析
avg_age = df['age'].mean()
print(f"平均年龄: {avg_age}")

{"total_people": len(df), "avg_age": avg_age}
"""
)

print(f"数据处理结果: {data_result}")

print("\n=== 结果格式示例 ===")
# 展示不同格式的结果生成
format_result = sandbox.run_code(
    """
import matplotlib.pyplot as plt
import numpy as np
import json
import base64
import io

print("演示多种结果格式:")

# 1. 文本格式
text_result = "这是文本格式的结果示例"
print(f"文本: {text_result}")

# 2. JSON数据格式
json_data = {
    "test_name": "CodeInterpreter格式测试",
    "formats": ["text", "json", "html", "image"],
    "timestamp": "2024-09-17T10:30:00Z",
    "results": {
        "success": True,
        "format_count": 4
    }
}
print(f"JSON: {json.dumps(json_data, ensure_ascii=False, indent=2)}")

# 3. HTML格式示例
html_content = \"\"\"
<div class="result-demo">
    <h3>CodeInterpreter 结果格式演示</h3>
    <p><strong>状态:</strong> <span style="color: green;">成功</span></p>
    <ul>
        <li>文本格式支持</li>
        <li>JSON数据结构</li>
        <li>HTML内容渲染</li>
        <li>图像base64编码</li>
    </ul>
</div>
\"\"\"
print(f"HTML: {html_content[:100]}...")

# 4. 简单图像生成
fig, ax = plt.subplots(1, 1, figsize=(6, 4))
x = np.linspace(0, 2*np.pi, 50)
y = np.sin(x)
ax.plot(x, y, 'b-', linewidth=2)
ax.set_title('简单正弦波示例')
ax.grid(True)

# 转换为base64
img_buffer = io.BytesIO()
plt.savefig(img_buffer, format='png', dpi=80, bbox_inches='tight')
img_buffer.seek(0)
img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
img_buffer.close()
plt.close()

print(f"图像: PNG base64编码 ({len(img_base64)} 字符)")

# 返回综合结果
{
    "text": text_result,
    "json_data": json_data,
    "html": html_content,
    "png_base64": img_base64[:50] + "...",  # 只显示前50个字符
    "summary": {
        "formats_demonstrated": 4,
        "total_size": len(text_result) + len(str(json_data)) + len(html_content) + len(img_base64),
        "description": "多格式结果演示完成"
    }
}
"""
)

print(f"结果格式测试: {format_result}")

print("\n=== 测试完成 ===")
print("CodeInterpreter基础功能测试完成!")
