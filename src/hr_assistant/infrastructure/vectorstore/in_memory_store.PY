from uuid import uuid4

import numpy as np

from src.hr_assistant.infrastructure.vectorstore.base import VectorStore

from dataclasses import dataclass

@dataclass
class ChunkMetadata:
    chunk_id: str | None
    filename: str
    index: int

@dataclass
class VectorRecord:
    id: str
    document_id: str
    content: str
    embedding: list[float]
    metadata: ChunkMetadata | None = None

class InMemoryStore(VectorStore):

    def __init__(self):
        self.vectors: list[VectorRecord] = []

    async def add(
        self,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: ChunkMetadata | None = None,
    ) -> None:

        self.vectors.append(
            VectorRecord(
                id=str(uuid4()),
                document_id=document_id,
                content=content,
                embedding=embedding,
                metadata=metadata
            )
        )

    async def search(
        self,
        embedding: list[float],
        top_k: int = 3
    ) -> list[VectorRecord]:
        
        results = []
        for document in self.vectors:
            score  = self._cosine_similarity(
                embedding,
                document.embedding
            )

            results.append((score, document))

        results.sort(key=lambda x: x[0], reverse=True)
                
        return [doc for _, doc in results[:top_k]]

    def _cosine_similarity(
        self,
        a: list[float],
        b: list[float],
    ) -> float:

        a = np.array(a)
        b = np.array(b)

        denom = np.linalg.norm(a) * np.linalg.norm(b)

        if denom == 0:
            return 0.0

        return float(np.dot(a, b) / denom)