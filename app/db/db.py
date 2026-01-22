from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///./todos.db", future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
