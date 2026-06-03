from fastapi import UploadFile

from src.hr_assistant.domain.entities.document_entity import Document

class IngestDocumentUseCase:

    def __init__(
        self,
        document_repository,
    ):
        self.document_repository = document_repository

    async def execute(
        self,
        file: UploadFile,
    ):

        content = await file.read()

        document = Document(
            filename=file.filename,
            content=content.decode("utf-8"),
        )

        await self.document_repository.save(
            document
        )

        return document