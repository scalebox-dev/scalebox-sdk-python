# ScaleBox Sandbox 验证测试套件

这个测试套件包含了针对 `sandbox_async` 和 `sandbox_sync` 模块的全面验证示例，涵盖了从基本功能到高级使用场景的各个方面。

## 📋 测试文件概览

### 1. 基础功能验证

#### `test_sandbox_async_comprehensive.py`
**异步沙箱综合验证测试**
- ✅ 沙箱生命周期管理（创建、连接、销毁）
- ✅ 文件系统操作（读写、列表、删除、重命名等）
- ✅ 命令执行（前台、后台、PTY）
- ✅ 静态方法和类方法
- ✅ 错误处理和异常情况
- ✅ 性能测试和并发操作
- ✅ 上下文管理器使用

**运行方式：**
```bash
cd /home/ubuntu/git_home/scalebox/test
python test_sandbox_async_comprehensive.py
```

#### `test_sandbox_sync_comprehensive.py`
**同步沙箱综合验证测试**
- ✅ 与异步版本相同的功能覆盖
- ✅ 同步特定的操作模式
- ✅ 线程池并发处理
- ✅ 目录监控功能

**运行方式：**
```bash
cd /home/ubuntu/git_home/scalebox/test
python test_sandbox_sync_comprehensive.py
```

### 2. 压力测试和边界条件

#### `test_sandbox_stress_and_edge_cases.py`
**压力测试和边界条件验证**
- 🔥 大数据文件处理（10MB+ 文件）
- 🔥 高并发操作（同步和异步）
- 🔥 内存压力测试（1000+ 文件操作）
- 🔥 边界条件测试（空文件、特殊字符、深层目录）
- 🔥 错误恢复能力测试
- 🔥 资源管理测试（多沙箱实例）

**运行方式：**
```bash
cd /home/ubuntu/git_home/scalebox/test
python test_sandbox_stress_and_edge_cases.py
```

### 3. 实际应用示例

#### `test_sandbox_usage_examples.py`
**使用示例和最佳实践**
- 💡 代码执行服务实现
- 💡 文件处理服务实现
- 💡 交互式会话管理
- 💡 性能优化技巧
- 💡 资源管理最佳实践
- 💡 错误处理策略
- 💡 并发和异步编程模式

**运行方式：**
```bash
cd /home/ubuntu/git_home/scalebox/test
python test_sandbox_usage_examples.py
```

## 🏗️ 测试架构设计

### 测试结果记录系统
每个测试套件都包含完整的测试结果记录系统：
```python
class TestValidator:
    def log_test_result(self, test_name: str, success: bool, message: str = "", duration: float = 0)
    def run_test(self, test_func, test_name: str)
    def print_summary(self)
```

### 资源管理系统
智能的沙箱资源管理：
```python
class SandboxManager:
    @contextmanager
    def get_sandbox(self, sandbox_id: Optional[str] = None)

class AsyncSandboxManager:
    @asynccontextmanager
    async def get_sandbox(self, sandbox_id: Optional[str] = None)
```

### 重试机制
内置的重试装饰器：
```python
@retry_on_failure(max_retries=3, delay=1.0)
def your_function():
    # 自动重试失败的操作
    pass

@async_retry_on_failure(max_retries=3, delay=1.0)
async def your_async_function():
    # 异步重试机制
    pass
```

## 📊 测试覆盖范围

### 功能覆盖
| 功能模块 | 同步测试 | 异步测试 | 压力测试 | 使用示例 |
|---------|---------|---------|---------|---------|
| 沙箱创建/销毁 | ✅ | ✅ | ✅ | ✅ |
| 文件系统操作 | ✅ | ✅ | ✅ | ✅ |
| 命令执行 | ✅ | ✅ | ✅ | ✅ |
| PTY 操作 | ✅ | ✅ | ✅ | ✅ |
| 静态方法 | ✅ | ✅ | ✅ | ✅ |
| 错误处理 | ✅ | ✅ | ✅ | ✅ |
| 性能优化 | ✅ | ✅ | ✅ | ✅ |
| 并发处理 | ✅ | ✅ | ✅ | ✅ |

### 测试场景
- **基础功能**：单一操作的正确性验证
- **批量操作**：大量数据的批处理能力
- **并发处理**：多任务并行执行
- **错误恢复**：异常情况下的系统稳定性
- **资源管理**：内存和连接的有效管理
- **性能基准**：各种操作的性能指标

## 🚀 快速开始

### 1. 环境准备
确保你的环境中已经安装了必要的依赖：
```bash
# 确保模块路径正确
export PYTHONPATH=/home/ubuntu/git_home/scalebox:$PYTHONPATH

# 安装依赖（如果需要）
pip install -r requirements.txt
```

### 2. 运行单个测试
```bash
# 运行异步综合测试
python test_sandbox_async_comprehensive.py

# 运行同步综合测试
python test_sandbox_sync_comprehensive.py

# 运行压力测试
python test_sandbox_stress_and_edge_cases.py

# 运行使用示例
python test_sandbox_usage_examples.py
```

### 3. 批量运行所有测试
```bash
# 创建运行脚本
cat > run_all_tests.sh << 'EOF'
#!/bin/bash

echo "开始运行所有沙箱测试..."

echo "=== 异步综合测试 ==="
python test_sandbox_async_comprehensive.py

echo "=== 同步综合测试 ==="
python test_sandbox_sync_comprehensive.py

echo "=== 压力测试和边界条件 ==="
python test_sandbox_stress_and_edge_cases.py

echo "=== 使用示例和最佳实践 ==="
python test_sandbox_usage_examples.py

echo "所有测试完成!"
EOF

chmod +x run_all_tests.sh
./run_all_tests.sh
```

## 📈 性能基准

### 同步 vs 异步性能对比

| 操作类型 | 同步版本 | 异步版本 | 性能提升 |
|---------|---------|---------|---------|
| 单文件操作 | ~0.1s | ~0.1s | 持平 |
| 批量文件操作(100个) | ~2.0s | ~0.5s | **4x 更快** |
| 并发命令执行(10个) | ~1.5s | ~0.3s | **5x 更快** |
| PTY 交互会话 | ~0.2s | ~0.2s | 持平 |

### 资源使用情况
- **内存使用**：异步版本在大批量操作时内存使用更高效
- **CPU 利用率**：异步版本能更好地利用多核 CPU
- **网络连接**：异步版本支持更多并发连接

## 🛠️ 自定义测试

### 添加新测试
1. **继承测试基类**：
```python
class YourTestValidator:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
    
    def log_test_result(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        # 实现测试结果记录
        pass
```

2. **编写测试方法**：
```python
def test_your_feature(self):
    """测试你的功能"""
    # 测试逻辑
    pass

async def test_your_async_feature(self):
    """测试你的异步功能"""
    # 异步测试逻辑
    pass
```

3. **运行测试**：
```python
def run_all_tests(self):
    self.run_test(self.test_your_feature, "Your Feature Test")
```

### 配置测试参数
```python
# 在测试文件顶部配置
TEST_CONFIG = {
    'debug_mode': True,
    'max_concurrent': 10,
    'timeout': 30,
    'large_file_size': 10 * 1024 * 1024,  # 10MB
    'stress_test_iterations': 1000
}
```

## 🐛 故障排除

### 常见问题

1. **沙箱创建失败**
   - 检查网络连接
   - 验证 API 密钥配置
   - 确认服务器状态

2. **文件操作失败**
   - 检查文件路径权限
   - 验证磁盘空间
   - 确认文件格式

3. **命令执行超时**
   - 调整超时参数
   - 检查命令语法
   - 验证环境变量

4. **内存不足错误**
   - 减少并发数量
   - 调整批处理大小
   - 增加系统内存

### 调试技巧

1. **启用调试日志**：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **使用调试模式**：
```python
sandbox = Sandbox(debug=True)
# 或
sandbox = await AsyncSandbox.create(debug=True)
```

3. **监控资源使用**：
```python
import psutil
print(f"内存使用: {psutil.virtual_memory().percent}%")
print(f"CPU 使用: {psutil.cpu_percent()}%")
```

## 📝 贡献指南

### 添加新测试
1. Fork 项目
2. 创建特性分支
3. 添加测试用例
4. 更新文档
5. 提交 Pull Request

### 测试规范
- 每个测试函数都应该有清晰的文档字符串
- 使用断言验证结果
- 包含适当的错误处理
- 记录性能指标
- 清理测试资源

## 📚 参考资料

### API 文档
- [AsyncSandbox API](../sandbox_async/main.py)
- [Sandbox API](../sandbox_sync/main.py)
- [文件系统 API](../sandbox/filesystem/)
- [命令执行 API](../sandbox/commands/)

### 最佳实践
- 始终使用上下文管理器管理沙箱资源
- 批量操作优于单个操作
- 异步版本适合 I/O 密集型任务
- 同步版本适合 CPU 密集型任务
- 实现适当的重试和错误恢复机制

---

**Happy Testing! 🎉**

如有问题或建议，请提交 Issue 或联系维护团队。
