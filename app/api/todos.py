import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.crud
from app.db.db import get_session
from app.services.background import background_task
from app.nats.client import nats_client
from app.services.schemas import HealthResponse, TaskRead, TaskCreate, TaskUpdate
from app.services.crud import get_tasks, get_task, create_task, update_task

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.post("/force-fetch", summary="Вызов фоновой задачи")
async def run_task(session: AsyncSession = Depends(get_session)):
    asyncio.create_task(background_task.run_once())
    return {"status": "started"}

@router.get("/health", response_model=HealthResponse, summary="соединение NATS")
async def health(session: AsyncSession = Depends(get_session)):
    nats_connected = False
    try:
        nats_connected = bool(nats_client.nc and getattr(nats_client.nc, 'is_connected', False))
    except Exception:
        nats_connected = False

    return {
        "nats_connected": nats_connected
    }

@router.get("/", response_model=List[TaskRead], summary="Получить все todo")
async def read_tasks(session: AsyncSession = Depends(get_session)):
    return await get_tasks(session)

@router.get("/{item_id}", response_model=TaskRead, summary="Получить todo по ID")
async def read_task(item_id: int, session: AsyncSession = Depends(get_session)):
    task = await get_task(session, item_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=TaskRead, summary="Создать новую todo")
async def create_task(item: TaskCreate, session: AsyncSession = Depends(get_session)):
    return await create_task(session, item)

@router.put("/{item_id}", response_model=TaskRead, summary="Обновить todo по ID")
async def update_task(item_id: int, item: TaskUpdate, session: AsyncSession = Depends(get_session)):
    payload = item.model_dump(exclude_unset=True)
    return await update_task(session, item_id, payload)

@router.delete("/{item_id}", response_model=dict, summary="Удалить todo по ID")
async def delete_task(item_id: int, session: AsyncSession = Depends(get_session)):
    await app.services.crud.delete_task(session, item_id)
    return {"status": "deleted"}