from browser_use import Agent, BrowserProfile
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os, asyncio
from browser_use.llm import ChatOpenAI
import subprocess, pathlib

load_dotenv()
os.environ["PLAYWRIGHT_CHROMIUM_EXTRA_ARGS"] = (
    "--no-sandbox --disable-dev-shm-usage --disable-gpu --disable-software-rasterizer"
)

# 1. 正常实例化 ChatOpenAI
_chat = ChatOpenAI(
    model="Qwen/Qwen2.5-72B-Instruct",
    api_key="sk-nbxsvrydquzfkfrrnnuutnfchpghzeuxilgawvsjqzjhumkh",
    base_url="https://api.siliconflow.cn/v1",
    temperature=0.1,
)


llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-R1",
    api_key="sk-nbxsvrydquzfkfrrnnuutnfchpghzeuxilgawvsjqzjhumkh",
    base_url="https://api.siliconflow.cn/v1",
    temperature=0.7,
)


# 2. 包一层模型，补 .provider + 转发所有必要方法
class SiliconFlowModel:
    provider = "siliconflow"

    def __init__(self, chat: ChatOpenAI):
        self.chat = chat
        # 把 browser-use 可能用到的字段全部代理
        self.model_name = chat.model_name  # ← 新增
        self.model = chat.model_name  # ← 新增（防它再换字段）
        self.ainvoke = chat.ainvoke
        self.invoke = chat.invoke
        self.bind = chat.bind

    # === 同步 ===
    def invoke(self, *args, **kwargs):
        return self.chat.invoke(*args, **kwargs)

    # === 异步 ===
    async def ainvoke(self, *args, **kwargs):
        return await self.chat.ainvoke(*args, **kwargs)

    # 如有其他缺失方法，继续代理即可
    def bind(self, *args, **kwargs):
        return self.chat.bind(*args, **kwargs)


# llm = SiliconFlowModel(_chat)


# 3. 创建 Agent
async def main():
    # chrome_path = subprocess.check_output(
    #     ["which", "google-chrome-stable"], text=True
    # ).strip()
    # browser_profile = BrowserProfile(
    #     headless=True,  # 先跑通再改 False
    #     # executable_path="/usr/bin/google-chrome-stable",
    #     extra_args=[
    #         "--no-sandbox",
    #         "--disable-dev-shm-usage",
    #         "--disable-gpu",
    #         "--disable-software-rasterizer",
    #         "--remote-debugging-port=9222",
    #         "--remote-debugging-address=0.0.0.0",  # 允许所有地址连接
    #         "--user-data-dir=/tmp/chrome-manual-test"  # 指定用户数据目录
    #     ],
    # )
    # "--disable-dev-shm-usage",
    # "--disable-gpu",
    # "--disable-software-rasterizer",
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            proxy={
                "server": "http://net-proxy:80",
                "username": "sbx-jz9kgqolumvmfc7ds",
                "password": "npt-Vd4CpGtjBOQEI8wdBv3wSOd8P4Bup1NgfsM",
            },
            headless=False,
            args=[
                # '--no-sandbox',
                # '--disable-dev-shm-usage',
                # '--disable-gpu',
                # '--disable-extensions',
                # '--disable-background-timer-throttling',
                # '--disable-renderer-backgrounding',
                # '--disable-features=TranslateUI',
                "--disable-blink-features=AutomationControlled",  # 禁用自动化控制标志
                "--start-maximized",  # 最大化窗口
            ],
        )
        # task = """
        #     1. 打开淘宝官网 (taobao.com)
        #     2. 搜索"格力空调"
        #     3. 记录下第一款商品的价格和标题
        #     4. 打开京东官网 (jd.com)
        #     5. 同样搜索"格力空调"
        #     6. 记录下第一款商品的价格和标题
        #     7. 对比在两个平台上看到的第一个商品的价格
        #     """
        task = """
            1. 打开google搜索
            2、输入今日新闻
            3、输出第一条内容
            """
        # task = """
        #     1、打开新浪网(http://sina.cn/)
        #     2. 搜索"科技"
        #     3. 记录前10条记录
        #     """
        agent = Agent(
            task=task,
            llm=llm,
            # browser_profile=browser_profile,
            browser=browser,
            use_vision=False,
        )
        result = await agent.run()
        print("---------- 最终结果 ----------")
        print(result)
        await browser.close()


# if __name__ == "__main__":
#     asyncio.run(main())
loop = asyncio.get_event_loop()
if loop.is_closed():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(main())
finally:
    loop.close()
