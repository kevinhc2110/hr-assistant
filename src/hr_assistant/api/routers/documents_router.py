from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile
from fastapi import File

from src.hr_assistant.api.schemas.document_schema import UploadDocumentResponse
from src.hr_assistant.application.use_cases.ingest_document_use_case import IngestDocumentUseCase
from src.hr_assistant.core.dependencies import get_ingest_document_use_case

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    use_case: IngestDocumentUseCase = Depends(
        get_ingest_document_use_case
    ),
):

    document = await use_case.execute(
        file=file
    )

    return UploadDocumentResponse(
        id=document["id"],
        filename=document["filename"]
    )
