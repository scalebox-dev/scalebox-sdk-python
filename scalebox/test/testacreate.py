import asyncio
import time

from scalebox.sandbox_async import AsyncSandbox


async def main():
    sandbox = await AsyncSandbox.create(
        template="base",      # 或自定义模板名
        api_key="sk-Wk4IgtUYOqnttxGaxZmELEV4p2FXh15Evt0FIcSa",
        timeout=3600
    )
    print("✅ 沙箱已启动，sandbox_domain:", sandbox.sandbox_domain)
    print("✅ 沙箱已启动，ID:", sandbox.sandbox_id)
    print("✅ 沙箱已启动，connection_config:", sandbox.connection_config)
    print("✅ 沙箱已启动，envd_api_url:", sandbox.envd_api_url)
    time.sleep(20)
    sandboxMetrics = await sandbox.get_metrics()
    for metric in sandboxMetrics:
        print(metric)


if __name__ == "__main__":
    asyncio.run(main())