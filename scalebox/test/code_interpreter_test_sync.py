import asyncio
import time

from code_interpreter import Sandbox
# from scalebox.sandbox_async.main import AsyncSandbox

def pty_output_handler(output):
    """处理 PTY 输出的回调函数"""
    print(f"输出: {output}")

def main():
    sandbox = Sandbox(

    )
    proc= sandbox.run_code("""
import time
for i in range(3):
    print("Hello E2B", i)
    time.sleep(50)
""",language="python3",request_timeout=3600,
   on_stdout=pty_output_handler,
   on_stderr=pty_output_handler,
   on_result=pty_output_handler,)
    print(proc)
    time.sleep(10)

if __name__ == "__main__":
    main()
