from fastapi import APIRouter, WebSocket

from .manager import manager

router = APIRouter()


@router.websocket("/ws/todos")
async def ws_todos(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"echo: {data}")
    finally:
        await manager.disconnect(websocket)
