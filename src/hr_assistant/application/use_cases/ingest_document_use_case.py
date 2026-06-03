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

        # embedding = await self.embedding_provider.embed(
        #     document.content
        # )

        # await self.vector_store.add(
        #     document.id,
        #     document.content,
        #     embedding=embedding
        # )

        return document