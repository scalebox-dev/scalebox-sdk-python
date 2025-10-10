import asyncio

from scalebox.sandbox.commands.command_handle import PtySize
from sandbox_async.main import AsyncSandbox

# from scalebox.sandbox_async.main import AsyncSandbox


async def pty_output_handler(output):
    """处理 PTY 输出的回调函数"""
    print(f"PTY 输出: {output}")


async def main():
    sandbox = AsyncSandbox()
    proc = await sandbox.commands.run("echo hello from async")
    print("exit_code =", proc.exit_code)
    print("stdout   =", proc.stdout)
    # 4. 创建 PTY
    pty_size = PtySize(rows=24, cols=80)
    pty_handle = await sandbox.pty.create(
        size=pty_size,
        on_data=pty_output_handler,
        cwd="/root",
        envs={"CUSTOM_ENV": "value"},
        timeout=120,
        request_timeout=30,
    )
    print(f"PTY 已创建，PID: {pty_handle.pid}")

    # 5. 向 PTY 发送输入
    await sandbox.pty.send_stdin(
        pid=pty_handle.pid, data=b"echo 'Hello from PTY'\n", request_timeout=10
    )
    await asyncio.sleep(2)

    # 6. 调整 PTY 大小
    new_size = PtySize(rows=30, cols=100)
    await sandbox.pty.resize(pid=pty_handle.pid, size=new_size, request_timeout=10)
    print("PTY 大小已调整")
    killed = await sandbox.pty.kill(pty_handle.pid)
    print(f"PTY 是否被杀死: {killed}")


# 静态方法使用示例
async def static_methods_example():
    # 1. 创建沙箱
    sandbox = await AsyncSandbox.create()
    sandbox_id = sandbox.sandbox_id

    try:
        # 2. 使用静态方法获取沙箱信息
        info = await AsyncSandbox.get_info(sandbox_id)
        print(f"静态方法获取的沙箱信息: {info}")

        # 3. 使用静态方法设置超时
        await AsyncSandbox.set_timeout(sandbox_id, 1800)  # 30分钟

        # 4. 使用静态方法获取指标
        try:
            metrics = await AsyncSandbox.get_metrics(sandbox_id)
            print(f"静态方法获取的指标: {metrics}")
        except Exception as e:
            print(f"静态方法获取指标失败: {e}")

    finally:
        # 5. 使用静态方法关闭沙箱
        killed = await AsyncSandbox.kill(sandbox_id)
        print(f"静态方法关闭沙箱结果: {killed}")


# 连接现有沙箱示例
async def connect_example():
    # 1. 创建沙箱并获取ID
    sandbox = await AsyncSandbox.create()
    sandbox_id = sandbox.sandbox_id
    await sandbox.kill()  # 先关闭

    # 2. 连接到现有沙箱
    try:
        connected_sandbox = await AsyncSandbox.connect(sandbox_id)
        print(f"成功连接到沙箱: {connected_sandbox.sandbox_id}")

        # 使用连接的沙箱
        is_running = await connected_sandbox.is_running()
        print(f"连接后沙箱状态: {is_running}")

        await connected_sandbox.kill()
    except Exception as e:
        print(f"连接沙箱失败: {e}")


# 上下文管理器使用示例
async def context_manager_example():
    sandbox = AsyncSandbox()
    # async with AsyncSandbox() as sandbox:
    #     # 在上下文中使用沙箱
    #     is_running = await sandbox.is_running()
    #     print(f"上下文管理器中的沙箱状态: {is_running}")

    # 创建和使用 PTY
    pty_handle = await sandbox.pty.create(
        size=PtySize(rows=24, cols=80), on_data=pty_output_handler
    )

    # 发送命令
    await sandbox.pty.send_stdin(pty_handle.pid, b"ls -la\n")

    # 等待一段时间
    await asyncio.sleep(10)


if __name__ == "__main__":
    # asyncio.run(main())0
    # asyncio.run(static_methods_example())
    # asyncio.run(connect_example())
    asyncio.run(context_manager_example())
