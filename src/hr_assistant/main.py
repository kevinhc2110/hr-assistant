from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.hr_assistant.api.routers.chat_router import router as chat_router
from src.hr_assistant.api.routers.documents_router import router as document_router
from src.hr_assistant.core.config import settings
from src.hr_assistant.core.dependencies import database
from src.hr_assistant.core.dependencies import vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):

    await database.connect()

    vector_store.pool = database.pool

    yield

    await database.disconnect()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

app.include_router(chat_router)
app.include_router(document_router)

