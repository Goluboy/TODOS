from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.services import schemas


async def get_task(session: AsyncSession, item_id: int):
    q = await session.execute(select(models.Task).where(models.Task.id == item_id))
    return q.scalars().first()

async def get_tasks(session: AsyncSession):
    q = await session.execute(select(models.Task))
    return q.scalars().all()


async def create_task(session: AsyncSession, item: schemas.TaskCreate):
    db_item = models.Task(todo=item.todo, completed=item.completed, user_id=item.user_id, external_id=None)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def update_task(session: AsyncSession, item_id: int, payload: dict):
    await session.execute(update(models.Task).where(models.Task.id == item_id).values(**payload))
    await session.commit()
    return await get_task(session, item_id)


async def delete_task(session: AsyncSession, item_id: int):
    await session.execute(delete(models.Task).where(models.Task.id == item_id))
    await session.commit()
    return True
