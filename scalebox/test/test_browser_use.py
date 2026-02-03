import asyncio, openai
from browser_use import Agent, BrowserProfile

# 指向本地 adapter
openai.base_url = "http://localhost:8000/v1/"
openai.api_key = "dummy"

TASK = (
    "打开 https://www.baidu.com，"
    "输入“今日天气”并搜索，"
    "把第一条结果的标题复制出来。"
)


async def main():
    agent = Agent(
        task=TASK,
        browser_profile=BrowserProfile(headless=False),
        model="gpt-4",  # 欺骗 browser-use
    )
    result = await agent.run()
    print("---------- 最终结果 ----------")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
