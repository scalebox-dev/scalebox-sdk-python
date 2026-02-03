import time

from scalebox.sandbox.commands.command_handle import PtySize
from scalebox.sandbox_sync.main import Sandbox


def output_handler(output):
    """处理 输出的回调函数"""
    print(f"PTY 输出: {output}")


sandboxes = Sandbox.list()
print(sandboxes)
box = Sandbox.connect(sandbox_id="sbx-0b3ccqezz67asn3ax")
print(box.files.list("/"))
