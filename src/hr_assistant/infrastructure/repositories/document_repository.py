


from hr_assistant.domain.entities.document_entity import Document


class DocumentRepository:

    def __init__(self, db):
        self.db = db

    async def save_document(
        self,
        document: Document,
    ):
        await self.db.pool.execute(
            """
            INSERT INTO documents (
                id,
                filename,
                created_at
            )
            VALUES ($1, $2, $3)
            """,
            document.id,
            document.filename,
            document.created_at
        )

