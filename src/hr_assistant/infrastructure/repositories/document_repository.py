from src.hr_assistant.domain.entities.document_entity import Document


class DocumentRepository:

    async def save(
        self,
        document: Document,
    ) -> None:
        pass