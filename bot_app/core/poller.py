import asyncio
from asyncio import Task
from typing import Optional


class Poller:
    def __init__(self, app: "BotApplication"):
        self.app = app
        self.is_running = False
        self.poll_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self):
        if self.is_running:
            self.is_running = False
            await self.poll_task

    async def poll(self):
        while self.is_running:
            updates = await self.app.vk_api.poll()
            if updates:
                await self.app.bot_manager.handle_updates(updates)
