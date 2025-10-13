import asyncio
import time

from scalebox.code_interpreter import Sandbox

# from scalebox.sandbox_async.main import AsyncSandbox


async def pty_output_handler(output):
    """处理 PTY 输出的回调函数"""
    print(f"输出: {output}")


def main():
    sandbox = Sandbox()
    context = sandbox.create_code_context(language="python3")
    print(context.__dict__)


if __name__ == "__main__":
    main()
