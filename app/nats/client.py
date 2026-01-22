import json
import os

from nats.aio.client import Client as NATS

from app.ws.manager import manager


class NatsClient:
    def __init__(self):
        self.url = os.getenv("NATS_URL", "nats://127.0.0.1:4222")
        self.nc: NATS | None = None
        self._subs = []

    async def connect(self):
        self.nc = NATS()
        await self.nc.connect(servers=[self.url])
        await self.nc.subscribe("todo-updates", cb=self._on_message)

    async def _on_message(self, msg):
        data = json.loads(msg.data.decode())
        await manager.broadcast({"from_nats": True, "subject": msg.subject, "message": data})

    async def publish(self, subject: str, message: dict):
        if not self.nc or not self.nc.is_connected:
            return
        await self.nc.publish(subject, json.dumps(message).encode())

    async def close(self):
        if self.nc and self.nc.is_connected:
            await self.nc.drain()
            await self.nc.close()


nats_client = NatsClient()
