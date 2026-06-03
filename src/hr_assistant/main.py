from fastapi import FastAPI
from src.hr_assistant.api.routers.chat_router import router as chat_router
from src.hr_assistant.api.routers.documents_router import router as document_router
from src.hr_assistant.core.config import settings

app = FastAPI(
    title=settings.app_name,
)

app.include_router(chat_router)
app.include_router(document_router)

