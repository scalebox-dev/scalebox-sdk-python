#!/usr/bin/env python3
"""
Simple async CodeInterpreter test example.
Similar to testsandbox_async.py but for code interpreter functionality.
"""

import asyncio
from scalebox.code_interpreter import AsyncSandbox, Context


async def async_output_handler(output):
    """处理异步输出的回调函数"""
    print(f"异步输出: {output.content}")


async def async_result_handler(result):
    """处理异步结果的回调函数"""
    print(f"异步结果: {result}")


async def async_error_handler(error):
    """处理异步错误的回调函数"""
    print(f"异步错误: {error.name} - {error.value}")


async def main():
    # 创建异步代码解释器沙箱
    sandbox = AsyncSandbox(template="code-interpreter-v1")

    print("=== 基础异步Python代码执行 ===")
    # 基础异步Python代码执行
    result = await sandbox.run_code(
        """
import asyncio

print("开始异步代码执行")

async def async_task():
    print("异步任务开始")
    await asyncio.sleep(0.1)
    result = sum(range(10))
    print(f"异步任务完成，结果: {result}")
    return result

result = await async_task()
print(f"最终结果: {result}")
result
""",
        language="python",
    )

    print(f"异步执行结果: {result}")
    print(f"标准输出: {result.logs.stdout}")

    print("\n=== 并发代码执行 ===")
    # 并发执行多个代码片段
    codes = [
        """
import asyncio
print("任务1开始")
await asyncio.sleep(0.1)
result = {"task": 1, "value": 100}
print(f"任务1完成: {result}")
result
""",
        """
import asyncio
print("任务2开始")
await asyncio.sleep(0.1)
result = {"task": 2, "value": 200}
print(f"任务2完成: {result}")
result
""",
        """
import asyncio
print("任务3开始")
await asyncio.sleep(0.1)
result = {"task": 3, "value": 300}
print(f"任务3完成: {result}")
result
""",
    ]

    # 并发执行
    import time

    start_time = time.time()
    tasks = [sandbox.run_code(code) for code in codes]
    results = await asyncio.gather(*tasks)
    duration = time.time() - start_time

    print(f"并发执行完成，耗时: {duration:.3f}s")
    for i, result in enumerate(results):
        print(f"任务 {i+1} 结果: {result.logs.stdout}")

    print("\n=== 异步数据处理 ===")
    # 异步数据处理
    async_data_result = await sandbox.run_code(
        """
import asyncio
import pandas as pd
import json

async def process_data_async():
    print("开始异步数据处理")
    
    # 模拟异步数据获取
    await asyncio.sleep(0.05)
    
    data = {
        'id': range(1, 11),
        'value': [i * 10 for i in range(1, 11)],
        'category': ['A' if i % 2 == 0 else 'B' for i in range(1, 11)]
    }
    
    df = pd.DataFrame(data)
    print("数据处理完成")
    
    # 分析数据
    summary = {
        "total_rows": len(df),
        "avg_value": df['value'].mean(),
        "category_counts": df['category'].value_counts().to_dict()
    }
    
    return summary

result = await process_data_async()
print(f"异步数据处理结果: {json.dumps(result, indent=2)}")
result
"""
    )

    print(f"异步数据处理结果: {async_data_result}")

    print("\n=== 使用异步回调函数 ===")
    # 使用异步回调函数
    callback_result = await sandbox.run_code(
        """
import asyncio

print("开始执行带异步回调的代码")

async def async_workflow():
    for i in range(3):
        print(f"异步步骤 {i+1}")
        await asyncio.sleep(0.05)
    
    result = {"steps": 3, "status": "async_completed"}
    print(f"异步流程完成: {result}")
    return result

result = await async_workflow()
result
""",
        on_stdout=async_output_handler,
        on_result=async_result_handler,
        on_error=async_error_handler,
    )

    print("\n=== 异步上下文管理 ===")
    # 创建异步上下文
    context = await sandbox.create_code_context(language="python", cwd="/tmp")
    print(f"创建异步上下文: {context.id}")

    # 在异步上下文中执行代码
    context_result1 = await sandbox.run_code(
        """
import asyncio

# 在异步上下文中定义变量
async_context_var = "Hello from async context"
async_data = {"status": "initialized", "items": []}

async def add_item(item):
    async_data["items"].append(item)
    await asyncio.sleep(0.01)
    return len(async_data["items"])

# 添加一些项目
for i in range(3):
    count = await add_item(f"item_{i}")
    print(f"添加项目 {i}, 当前总数: {count}")

print(f"异步上下文变量: {async_context_var}")
print(f"异步数据: {async_data}")
""",
        context=context,
    )

    # 在同一异步上下文中使用变量
    context_result2 = await sandbox.run_code(
        """
print(f"从异步上下文读取: {async_context_var}")
print(f"当前数据: {async_data}")

# 继续处理数据
async def process_items():
    results = []
    for item in async_data["items"]:
        processed = f"processed_{item}"
        results.append(processed)
        await asyncio.sleep(0.01)
    return results

processed_items = await process_items()
async_data["processed"] = processed_items

print(f"处理完成: {len(processed_items)} 个项目")
{"original_items": len(async_data["items"]), "processed_items": len(processed_items)}
""",
        context=context,
    )

    print(f"异步上下文测试结果: {context_result2}")

    print("\n=== 异步错误处理示例 ===")
    # 异步错误处理
    async_error_result = await sandbox.run_code(
        """
import asyncio

async def failing_async_task():
    print("异步任务开始")
    await asyncio.sleep(0.1)
    # 这里会产生错误
    result = 10 / 0
    return result

print("开始可能失败的异步任务")
result = await failing_async_task()
""",
        on_error=async_error_handler,
    )

    print(f"异步错误处理结果: {async_error_result.error}")

    print("\n=== 异步批处理示例 ===")
    # 异步批处理
    batch_result = await sandbox.run_code(
        '''
import asyncio
import time

async def process_item(item_id):
    """处理单个项目"""
    await asyncio.sleep(0.02)  # 模拟处理时间
    return {"id": item_id, "processed": True, "value": item_id * 10}

async def batch_processor(items):
    """批量处理器"""
    print(f"开始批量处理 {len(items)} 个项目")
    start_time = time.time()
    
    # 并发处理所有项目
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    
    processing_time = time.time() - start_time
    print(f"批量处理完成，耗时: {processing_time:.3f}s")
    
    return {
        "processed_items": results,
        "processing_time": processing_time,
        "throughput": len(items) / processing_time
    }

# 处理一批项目
items_to_process = list(range(1, 11))  # 处理10个项目
result = await batch_processor(items_to_process)

print(f"批处理结果:")
print(f"  处理项目数: {len(result['processed_items'])}")
print(f"  处理时间: {result['processing_time']:.3f}s")
print(f"  吞吐量: {result['throughput']:.1f} items/s")

result
'''
    )

    print(f"异步批处理结果: {batch_result}")

    print("\n=== 异步结果格式示例 ===")
    # 展示异步多格式结果生成
    async_format_result = await sandbox.run_code(
        '''
import asyncio
import json
import base64
import matplotlib.pyplot as plt
import numpy as np
import io

async def generate_async_format_demo():
    print("开始异步多格式结果演示...")
    
    # 1. 异步文本生成
    await asyncio.sleep(0.05)
    text_content = """
异步CodeInterpreter多格式结果演示
================================
执行模式: 异步
生成时间: 2024-09-17
状态: 成功
    """
    print(f"异步文本格式生成完成")
    
    # 2. 异步JSON数据编译
    await asyncio.sleep(0.05)
    json_data = {
        "async_demo": {
            "execution_type": "asynchronous",
            "formats": ["text", "json", "html", "chart", "image"],
            "performance": {
                "concurrent_tasks": 3,
                "total_time": "< 0.5s",
                "efficiency": "高效"
            }
        },
        "results": {
            "format_count": 5,
            "async_benefits": [
                "非阻塞执行",
                "并发处理", 
                "资源优化"
            ]
        }
    }
    print(f"异步JSON数据生成完成")
    
    # 3. 异步HTML内容生成
    await asyncio.sleep(0.05)
    html_content = """
<div class="async-demo-results">
    <h2>异步CodeInterpreter演示</h2>
    <div class="async-status">
        <span class="badge success">异步执行成功</span>
    </div>
    <div class="format-list">
        <h3>支持的格式:</h3>
        <ul>
        <li>异步文本生成</li>
        <li>异步JSON编译</li>
        <li>异步HTML渲染</li>
        <li>异步图表数据</li>
        <li>异步图像处理</li>
        </ul>
    </div>
    <div class="performance-info">
        <p><strong>性能优势:</strong> 并发处理多种格式，显著提升效率</p>
    </div>
</div>
    """
    print(f"异步HTML内容生成完成")
    
    return {
        "text": text_content.strip(),
        "json_data": json_data,
        "html": html_content.strip(),
        "execution_summary": {
            "mode": "async",
            "formats_generated": 3,
            "performance": "excellent"
        }
    }

# 异步并发执行格式生成任务
async def concurrent_format_generation():
    # 并发生成多个格式的示例
    tasks = []
    
    # 任务1: 图表数据生成
    async def generate_chart_data():
        await asyncio.sleep(0.1)
        return {
            "type": "performance_chart",
            "data": {
                "labels": ["异步执行", "同步执行"],
                "values": [95, 65],
                "colors": ["#28a745", "#6c757d"]
            },
            "description": "异步vs同步性能对比"
        }
    
    # 任务2: 数据统计
    async def generate_statistics():
        await asyncio.sleep(0.08)
        return {
            "execution_stats": {
                "total_formats": 5,
                "async_tasks": 3,
                "completion_rate": "100%",
                "average_response_time": "0.087s"
            }
        }
    
    # 任务3: 简单图像处理
    async def generate_simple_chart():
        await asyncio.sleep(0.12)
        
        # 在异步任务中生成图像
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 异步性能对比数据
        categories = ['文本', 'JSON', 'HTML', '图表', '图像']
        async_times = [0.05, 0.05, 0.05, 0.10, 0.12]
        sync_times = [0.02, 0.03, 0.02, 0.15, 0.18]
        
        x = np.arange(len(categories))
        width = 0.35
        
        ax.bar(x - width/2, async_times, width, label='异步执行', color='#28a745', alpha=0.8)
        ax.bar(x + width/2, sync_times, width, label='同步执行', color='#6c757d', alpha=0.8)
        
        ax.set_xlabel('结果格式类型')
        ax.set_ylabel('执行时间 (秒)')
        ax.set_title('异步vs同步格式生成性能对比')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 转换为base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        img_buffer.close()
        plt.close()
        
        return {
            "image_data": img_base64,
            "format": "png_base64",
            "size": len(img_base64),
            "description": "异步vs同步性能对比图表"
        }
    
    # 并发执行所有任务
    print("启动并发格式生成任务...")
    chart_task = asyncio.create_task(generate_chart_data())
    stats_task = asyncio.create_task(generate_statistics())
    image_task = asyncio.create_task(generate_simple_chart())
    
    chart_data, statistics, image_data = await asyncio.gather(
        chart_task, stats_task, image_task
    )
    
    print("所有并发任务完成")
    
    return {
        "chart_data": chart_data,
        "statistics": statistics,
        "image_result": {
            "size": image_data["size"],
            "format": image_data["format"],
            "description": image_data["description"]
        }
    }

# 执行异步格式演示
print("开始异步结果格式演示...")

# 1. 基础格式生成
basic_formats = await generate_async_format_demo()
print(f"基础格式生成完成: {list(basic_formats.keys())}")

# 2. 并发格式生成
concurrent_results = await concurrent_format_generation()
print(f"并发格式生成完成")

# 综合结果
final_result = {
    "demo_type": "async_multi_format",
    "basic_formats": basic_formats,
    "concurrent_results": concurrent_results,
    "summary": {
        "total_format_types": 7,
        "concurrent_tasks": 3,
        "execution_mode": "fully_asynchronous",
        "performance_rating": "优秀",
        "async_advantages": [
            "并发执行多种格式生成",
            "非阻塞I/O操作",
            "高效的资源利用",
            "优秀的响应时间"
        ]
    }
}

print("\\n异步多格式结果演示完成!")
final_result
'''
    )

    print(f"异步格式结果测试: {async_format_result}")

    print("\n=== 异步测试完成 ===")
    print("AsyncCodeInterpreter功能测试完成!")

    # 清理
    await sandbox.kill()


if __name__ == "__main__":
    asyncio.run(main())
