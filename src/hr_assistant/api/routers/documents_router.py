from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile
from fastapi import File

from src.hr_assistant.core.dependencies import get_ingest_document_use_case, get_vector_store
from src.hr_assistant.infrastructure.vectorstore.in_memory_store import InMemoryStore

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    use_case=Depends(
        get_ingest_document_use_case
    ),
):

    document = await use_case.execute(
        file=file
    )

    return {
        "id": document.id,
        "filename": document.filename
    }
