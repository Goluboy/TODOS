import asyncio
import json
from typing import Set

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self.connections.discard(websocket)

    async def send_json(self, websocket: WebSocket, message: dict):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        to_remove = []
        async with self._lock:
            for ws in list(self.connections):
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    to_remove.append(ws)
            for ws in to_remove:
                self.connections.discard(ws)


manager = WebSocketManager()
