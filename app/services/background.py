import asyncio
from typing import Optional

import httpx

from app.db.db import AsyncSessionLocal
from app.services.crud import create_task, update_task, get_task
from app.services.schemas import TaskCreate
from app.nats.client import nats_client
from app.ws.manager import manager


class BackgroundTask:
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()
        self.url = "https://dummyjson.com/todos"
        self.interval = 60

    async def _loop(self):
        while not self._stop.is_set():
            await self._run_once_internal()
            await asyncio.wait([self._stop.wait()], timeout=self.interval)

    async def _run_once_internal(self):
        todos = None
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(self.url, timeout=20.0)
                r.raise_for_status()
                payload = r.json()
                todos = payload.get("todos", [])
        except httpx.RequestError as exc:
            out = {"event": "fetch_failed", "error": str(exc)}
            await nats_client.publish("todo-updates", out)
            await manager.broadcast(out)
            return
            
        async with AsyncSessionLocal() as session:
            for todo_data in todos:
                external_id = todo_data.get("id")
                existing = await get_task(session, external_id)
                if existing:
                    await update_task(session, existing.id, {
                        "todo": todo_data.get("todo", ""),
                        "completed": todo_data.get("completed", False),
                    })
                else:
                    task_create = TaskCreate(
                        todo=todo_data.get("todo", ""),
                        completed=todo_data.get("completed", False),
                        user_id=todo_data.get("userId", 1),
                    )
                    new_task = await create_task(session, task_create)
                    await update_task(session, new_task.id, {"external_id": external_id})
            
            out = {"event": "fetch_success", "count": len(todos)}
            await nats_client.publish("todo-updates", out)
            await manager.broadcast(out)


    async def run_once(self):
        await self._run_once_internal()

    async def start(self):
        if self._task and not self._task.done():
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self._stop.set()
        if self._task:
            await self._task


background_task = BackgroundTask()
