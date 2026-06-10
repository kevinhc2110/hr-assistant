from hr_assistant.domain.entities.document_entity import Document
from hr_assistant.domain.repositories.document_repository import (
    DocumentRepository as DocumentRepositoryInterface,
)


class DocumentRepository(DocumentRepositoryInterface):

    def __init__(self, db):
        self.db = db

    async def save(self, document: Document) -> None:
        await self.db.execute(
            """
            INSERT INTO documents (id, filename, created_at)
            VALUES ($1, $2, $3)
            """,
            document.id,
            document.filename,
            document.created_at,
        )
