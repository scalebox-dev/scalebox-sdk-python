#!/usr/bin/env python3
"""
Minimal async test for sandbox_async.filesystem.watch_dir.
Creates an AsyncSandbox, watches a temp directory, writes a file to trigger
an event, asserts events were received, and cleans up.
"""

import asyncio
import time
import logging
from typing import List

from scalebox.sandbox_async.main import AsyncSandbox
from scalebox.sandbox.filesystem.watch_handle import FilesystemEvent


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    async with await AsyncSandbox.create(
        template="base", timeout=300, metadata={"test": "watch_dir_async"}
    ) as sandbox:
        watch_path = "/tmp/watch_async_test"
        await sandbox.files.make_dir(watch_path)

        events: List[FilesystemEvent] = []

        async def on_event(ev: FilesystemEvent):
            print(ev)
            events.append(ev)

        # Start watching directory
        handle = await sandbox.files.watch_dir(
            path=watch_path,
            on_event=on_event,
            timeout=10,
            recursive=False,
        )

        # Trigger a filesystem event
        await sandbox.files.write(f"{watch_path}/new_file.txt", "content")

        # Wait a bit for event propagation
        await asyncio.sleep(2)

        # Stop watching
        await handle.stop()

        logger.info(f"Received {len(events)} filesystem events")
        assert len(events) >= 1


if __name__ == "__main__":
    asyncio.run(main())
