import asyncio
import time

from sandbox_async import AsyncSandbox


async def main():
    sandbox = await AsyncSandbox.get_info(
        sandbox_id="",
        api_key="sk-Wk4IgtUYOqnttxGaxZmELEV4p2FXh15Evt0FIcSa"
    )
    print("✅ 沙箱已启动，sandbox_domain:", sandbox.sandbox_domain)
    print("✅ 沙箱已启动，ID:", sandbox.sandbox_id)
    print("✅ 沙箱已启动，connection_config:", sandbox.name)
    print("✅ 沙箱已启动，envd_api_url:", sandbox.started_at)


if __name__ == "__main__":
    asyncio.run(main())