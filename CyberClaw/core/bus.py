import asyncio


task_queue = asyncio.Queue()

async def emit_task(content: str):
    await task_queue.put(content)