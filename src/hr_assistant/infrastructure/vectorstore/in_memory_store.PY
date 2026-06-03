import numpy as np

from src.hr_assistant.infrastructure.vectorstore.base import VectorStore


class InMemoryStore(VectorStore):

    def __init__(self):
        self.documents = []

    async def add(
        self,
        document_id: str,
        content: str,
        embedding: list[float]
    ) -> None:

        self.documents.append({
            'id': document_id,
            'content': content,
            'embedding': embedding,
        })

    async def search(
        self,
        embedding: list[float],
        top_k: int = 3
    ) -> list[dict]:
        
        results = []
        for document in self.documents:
            score  = self._cosine_similarity(
                embedding,
                document['embedding']
            )
            results.append({
                score,
                document
            })

        results.sort(
            key=lambda x: x[0],
            reverse=True,
        )
                
        return [
            item[1]
            for item in results[:top_k]
        ]

    def _cosine_similarity(
        self,
        a: list[float],
        b: list[float],
    ) -> float:

        a = np.array(a)
        b = np.array(b)

        return np.dot(a, b) / (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )