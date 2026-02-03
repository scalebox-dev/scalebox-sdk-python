import time

from scalebox.sandbox.commands.command_handle import PtySize
from scalebox.sandbox_sync.main import Sandbox


def output_handler(output):
    """处理 输出的回调函数"""
    print(f"PTY 输出: {output}")


sandbox = Sandbox.create(api_key=f"sk-Wk4Ig")
# print(sandbox.files.list("/root",2))
# proc = sandbox.commands._start(
#         cmd="python3 -c \"import math; print('π =', math.pi); exit(42)\"",
#     ).wait(on_pty=None,
#            on_stdout=lambda data: print("[STDOUT]", data, end=""),
#            on_stderr=lambda data: print("[STDERR]", data, end=""),)

# proc = sandbox.commands._start(
#         cmd="ls /",
#     ).wait(on_pty=None,
#            on_stdout=lambda data: print("[STDOUT]", data, end=""),
#            on_stderr=lambda data: print("[STDERR]", data, end=""),)
#
# print("exit_code =", proc.exit_code)   # 42
# print("full_output =", proc.stdout)    # π = 3.141592653589793
# pty=sandbox.pty.create(size=PtySize(1024, 768),user="root",cwd="/root/",)
# sandbox.pty.send_stdin(pid=pty.pid,data=b"echo \"hello\"")
# sandbox.pty.send_stdin(pid=pty.pid,data=b"echo \"world!\"")
# result=pty.wait(
#     on_pty=lambda data: print("[STDOUT]", data, end=""),
# )
# print("exit_code =", result.exit_code)
# print("full_output =", result.stdout)
result = sandbox.commands.run(
    cmd="ls /", on_stdout=output_handler, on_stderr=output_handler
)
print(result.exit_code)
print(result.error)
pty = sandbox.pty.create(
    size=PtySize(1024, 768), user="root", cwd="/root/", request_timeout=3600
)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "hello"')
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!"')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 30s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 60s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 90s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 120s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 150s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 180s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 210s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 240s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 270s')
time.sleep(30)
sandbox.pty.send_stdin(pid=pty.pid, data=b'echo "world!" 300s')
result = pty.wait(
    on_pty=lambda data: print("[STDOUT]", data, end=""),
)
print("exit_code =", result.exit_code)
print("full_output =", result.stdout)
# result=sandbox.commands.run(cmd="ls /",
#                      on_stdout=output_handler,
#                      on_stderr=output_handler)
# print(result.exit_code)
# print(result.error)
