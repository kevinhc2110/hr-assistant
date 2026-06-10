from abc import ABC, abstractmethod

from hr_assistant.domain.entities.document_entity import Document


class DocumentRepository(ABC):

    @abstractmethod
    async def save(self, document: Document) -> None:
        pass
