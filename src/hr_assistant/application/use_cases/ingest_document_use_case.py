from datetime import datetime, timezone
from uuid import uuid4
from fastapi import UploadFile

from src.hr_assistant.domain.entities.document_entity import Document

class IngestDocumentUseCase:

    def __init__(
        self,
        document_repository,
        embedding_provider,
        vector_store
    ):
        self.document_repository = document_repository
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def execute(self, file: UploadFile):

        content = await file.read()

        document = Document(
            id=str(uuid4()),
            filename=file.filename,
            created_at=datetime.now(timezone.utc)
        )

        await self.document_repository.save_document(document)

        texts = self._split_document(content.decode("utf-8"))

        for index, text in enumerate(texts):

            embedding = await self.embedding_provider.embed(
                text
            )

            await self.vector_store.add(
                document_id=document.id,
                content=text,
                embedding=embedding,
                metadata={
                    "filename": document.filename,
                    "index": index
                },
            )

        return document


    def _split_document(self, text: str, size: int = 500) -> list[str]:

        return [
            text[i:i + size]
            for i in range(0, len(text), size)
        ]