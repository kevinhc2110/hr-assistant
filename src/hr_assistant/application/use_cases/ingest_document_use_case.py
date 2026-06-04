from datetime import datetime, timezone
from uuid import uuid4
from fastapi import UploadFile

from src.hr_assistant.domain.entities.chunk_entity import DocumentChunk
from src.hr_assistant.domain.entities.document_entity import Document
from src.hr_assistant.infrastructure.vectorstore.in_memory_store import ChunkMetadata


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
            content=content.decode("utf-8"),
            created_at=datetime.now(timezone.utc)
        )

        await self.document_repository.save_document(document)

        chunks = self._chunk_document(document)

        for chunk in chunks:

            await self.document_repository.save_chunk(chunk)

            embedding = await self.embedding_provider.embed(
                chunk.content
            )

            await self.vector_store.add(
                document_id=chunk.document_id,
                content=chunk.content,
                embedding=embedding,
                metadata=ChunkMetadata(
                    chunk_id=chunk.id,
                    filename=document.filename,
                    index=chunk.index
                )
            )

        return document

    def _chunk_document(self, document: Document) -> list[DocumentChunk]:

        texts = self._split_document(document.content)

        return [
            DocumentChunk(
                id=str(uuid4()),
                document_id=document.id,
                content=text,
                index=i
            )
            for i, text in enumerate(texts)
        ]

    def _split_document(self, text: str, size: int = 500) -> list[str]:

        return [
            text[i:i + size]
            for i in range(0, len(text), size)
        ]