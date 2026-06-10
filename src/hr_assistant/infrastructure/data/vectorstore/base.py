from abc import ABC, abstractmethod

from hr_assistant.domain.models.chunk_record import ChunkRecord


class VectorStore(ABC):

    @abstractmethod
    async def add(
        self,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:
        pass

    @abstractmethod
    async def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[ChunkRecord]:
        pass
