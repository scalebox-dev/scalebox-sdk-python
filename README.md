# Scalebox Python SDK

一个用于在可控沙箱中执行多语言代码的 Python SDK，支持同步与异步模式，以及多语言 Kernel（Python、R、Node.js、Deno/TypeScript、Java/IJAVA、Bash）。已提供全面的真实环境测试用例与脚本。

## 功能特性
- 多语言内核：Python、R、Node.js、Deno/TypeScript、Java/IJAVA、Bash
- 同步 `Sandbox` 与异步 `AsyncSandbox` 执行
- 持久上下文：跨多次执行保留变量/状态
- 回调订阅：stdout、stderr、结果与错误
- 丰富结果格式：text、html、markdown、svg、png、jpeg、pdf、latex、json、javascript、chart、data 等
- 真实环境测试：覆盖同步/异步与多语言示例

## 环境要求
- Python 3.12+
- 可访问的 Scalebox 环境或本地服务

## 安装

```bash
# 克隆项目
git clone https://github.com/scalebox-dev/scalebox-sdk-python.git
cd scalebox-sdk-python

# 建议使用虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r scalebox/requirements.txt
```

如果你以源码方式直接使用包（非 pip 安装），请将 `scalebox` 目录加入 Python 路径或复制到 venv 的 site-packages：
```bash
cp -r scalebox venv/lib/python3.12/site-packages/
```

## 配置
支持从环境变量或 `.env` 文件读取凭据：

- `SBX_API_KEY` 或 `E2B_API_KEY`

示例：
```env
# .env
SBX_API_KEY=***
```
或：
```bash
export SBX_API_KEY=***
```

可选：使用 `python-dotenv` 自动加载 `.env`：
```bash
pip install python-dotenv
```

## 快速开始（同步）
```python
from dotenv import load_dotenv; load_dotenv()
from scalebox.code_interpreter import Sandbox

sandbox = Sandbox.create()  # 默认生存期 5 分钟
execution = sandbox.run_code("print('hello world')", language="python")
print(execution.logs.stdout)

files = sandbox.files.list("/")
print(files)
```

## 快速开始（异步）
```python
import asyncio
from dotenv import load_dotenv; load_dotenv()
from scalebox.code_interpreter import AsyncSandbox

async def main():
    sandbox = await AsyncSandbox.create()
    exec_ = await sandbox.run_code("print('async hello')", language="python")
    print(exec_.logs.stdout)

asyncio.run(main())
```

## 多语言示例
- Python：`language="python"`
- R：`language="r"`
- Node.js：`language="nodejs"`
- Deno/TypeScript：`language="typescript"`
- Java（IJAVA/纯Java）：`language="ijava"` 或 `language="java"`
- Bash：`language="bash"`

示例（Node.js）：
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
code = """
console.log("Hello from Node.js!");
const x = 1 + 2; console.log(`x=${x}`);
"""
result = sbx.run_code(code, language="nodejs")
print(result.logs.stdout)
```

示例（R）：
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
code = """
print("Hello from R!")
x <- mean(c(1,2,3,4,5))
print(paste("mean:", x))
"""
res = sbx.run_code(code, language="r")
print(res.logs.stdout)
```

示例（Deno/TypeScript）：
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
ts = """
console.log("Hello from Deno/TypeScript!")
const nums: number[] = [1,2,3]
console.log(nums.reduce((a,b)=>a+b, 0))
"""
res = sbx.run_code(ts, language="typescript")
print(res.logs.stdout)
```

示例（Java/IJAVA）：
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
code = """
System.out.println("Hello from IJAVA!");
int a = 10, b = 20; System.out.println(a + b);
"""
res = sbx.run_code(code, language="java")
print(res.logs.stdout)
```

示例（Bash）：
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
res = sbx.run_code("echo 'Hello from Bash'", language="bash")
print(res.logs.stdout)
```

## 上下文管理（Context）
上下文允许跨多次执行复用变量/状态：
```python
from scalebox.code_interpreter import Sandbox
sbx = Sandbox.create()
ctx = sbx.create_code_context(language="python", cwd="/tmp")

sbx.run_code("counter = 0", context=ctx)
sbx.run_code("counter += 1; print(counter)", context=ctx)
# 使用完必须清理
sbx.destroy_context(ctx)
```
异步 API：
```python
from scalebox.code_interpreter import AsyncSandbox

async def demo():
    sbx = await AsyncSandbox.create()
    ctx = await sbx.create_code_context(language="python", cwd="/tmp")
    await sbx.run_code("counter = 0", context=ctx)
    await sbx.run_code("counter += 1; print(counter)", context=ctx)
    await sbx.destroy_context(ctx)
```

## 回调（可选）
```python
from scalebox.code_interpreter import Sandbox
from scalebox.code_interpreter import OutputMessage, Result, ExecutionError

sbx = Sandbox.create()

def on_stdout(msg: OutputMessage):
    print("STDOUT:", msg.content)

def on_stderr(msg: OutputMessage):
    print("STDERR:", msg.content)

def on_result(res: Result):
    print("RESULT formats:", list(res.formats()))

def on_error(err: ExecutionError):
    print("ERROR:", err.name, err.value)

sbx.run_code(
    "print('with callbacks')",
    language="python",
    on_stdout=on_stdout,
    on_stderr=on_stderr,
    on_result=on_result,
    on_error=on_error,
)
```

## 结果格式（Result）
`Result` 可能包含如下数据字段：
- `text`, `html`, `markdown`, `svg`, `png`, `jpeg`, `pdf`, `latex`
- `json_data`, `javascript`, `data`, `chart`
- `execution_count`, `is_main_result`, `extra`

可以通过 `list(result.formats())` 查看可用格式。

## 运行测试
项目 `test/` 目录包含全面的真实环境用例（非 unittest，直接脚本风格），覆盖：
- 同步与异步综合用例
- 多语言内核（Python、R、Node.js、Deno/TypeScript、Java/IJAVA、Bash）
- 上下文管理、回调与结果格式

运行语法检查：
```bash
cd test
python3 -m py_compile test_code_interpreter_sync_comprehensive.py
python3 -m py_compile test_code_interpreter_async_comprehensive.py
```

建议在虚拟环境中准备依赖并按需安装语言运行时（如 R、Node、Deno、JDK/IJAVA 等），确保各内核能够被后端执行。

## 常见问题（Troubleshooting）
- Import/依赖错误：请确认已激活 venv 并正确安装 `scalebox/requirements.txt` 所需依赖
- `ModuleNotFoundError`：在测试脚本中添加项目根路径到 `sys.path`，或从项目根目录运行
- 外部内核不可用：确保环境已安装对应语言运行时（R/Node/Deno/JDK）与后端已启用该内核
- 超时/网络：检查网络与后端服务可达性，必要时增大 `timeout`/`request_timeout`

## 许可证
本项目遵循项目仓库所附许可证（LICENSE）条款。