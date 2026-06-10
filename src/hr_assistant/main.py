from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from hr_assistant.api.routers.chat_router import router as chat_router
from hr_assistant.api.routers.documents_router import router as document_router
from hr_assistant.infrastructure.data.postgres import PostgresDatabase
from hr_assistant.infrastructure.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):

    db = PostgresDatabase(dsn=settings.postgres_dsn)
    await db.connect()

    app.state.db = db

    yield

    await db.disconnect()

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

app.include_router(chat_router)
app.include_router(document_router)

frontend_dist = Path(__file__).resolve().parent.parent.parent / "demo" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

