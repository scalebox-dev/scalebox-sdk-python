import asyncio
import os

# from browser_use import Agent, BrowserProfile
from scalebox.sandbox_async.main import AsyncSandbox

# 设置环境变量，避免浏览器启动问题
os.environ["BROWSER_USE_DISABLE_TELEMETRY"] = "1"


async def main():
    sandbox = await AsyncSandbox.create(
        timeout=3600,
        template="browser-use-headless",
    )
    proc = await sandbox.commands.run("echo hello from async")
    print("exit_code =", proc.exit_code)
    print("stdout   =", proc.stdout)

    # try:
    #     # 配置浏览器参数 - 使用更稳定的配置
    #     browser_profile = BrowserProfile(
    #         # 设置浏览器窗口大小
    #         viewport_width=1200,
    #         viewport_height=800,
    #         # 在服务器环境必须使用无头模式
    #         headless=True,
    #         # 禁用沙盒，提高容器兼容性
    #         sandbox=False,
    #         # 增加超时时间
    #         browser_launch_timeout=60000,  # 60秒
    #         # 禁用GPU加速（服务器环境推荐）
    #         gpu_acceleration=False,
    #     )
    #
    #     # 定义需要 agent 执行的任务
    #     task = """
    #     请打开百度首页 (https://www.baidu.com)，在搜索框中输入"今日天气"，然后进行搜索。
    #     请等待搜索结果页面加载完成。
    #     """
    #
    #     # 创建 Agent 实例
    #     agent = Agent(
    #         task=task,
    #         browser_profile=browser_profile,
    #     )
    #
    #     print("开始执行浏览器自动化任务...")
    #
    #     # 运行 Agent
    #     result = await agent.run()
    #     print(f"任务执行完成: {result}")
    #
    # except Exception as e:
    #     print(f"执行过程中出现错误: {e}")
    #     # 打印更详细的错误信息
    #     import traceback
    #     traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
