from src.hr_assistant.domain.entities.chunk_entity import DocumentChunk
from src.hr_assistant.domain.entities.document_entity import Document


class DocumentRepository:

    async def save_document(
        self,
        document: Document,
    ) -> None:
        pass

    async def save_chunk(
        self,
        chunk: DocumentChunk,
    ) -> None:
        pass