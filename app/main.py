import logging
from contextlib import asynccontextmanager

from app.api import todos

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.db import engine, Base
from app.ws import router as ws_router
from app.nats.client import nats_client
from app.services.background import background_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "todos", "description": "Operations with todos (CRUD)"}
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        await nats_client.connect()
    except Exception as e:
        logger.warning("Failed to connect to NATS: %s", e)
    await background_task.start()
    
    yield
    
    await background_task.stop()
    try:
        await nats_client.close()
    except Exception:
        pass


app = FastAPI(
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router)
app.include_router(ws_router.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
