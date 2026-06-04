import json

from src.hr_assistant.infrastructure.vectorstore.models import ChunkRecord


class PGVectorStore:
    def __init__(self, pool):
        self.pool = pool

    async def add(
        self,
        document_id: str,
        content: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:
        embedding_str = self._parse_embedding(embedding)

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO chunks (
                    document_id,
                    content,
                    embedding,
                    metadata
                )
                VALUES (
                    $1,
                    $2,
                    $3,
                    $4
                )
                """,
                document_id,
                content,
                embedding_str,
                json.dumps(metadata) if metadata else None
            )

    async def search(
        self,
        embedding: list[float],
        top_k: int = 5
    ) -> list[ChunkRecord]:
        
        embedding_str = self._parse_embedding(embedding)

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    id,
                    document_id,
                    content,
                    metadata,
                    embedding <-> $1 AS score
                FROM chunks
                ORDER BY score
                LIMIT $2;
                """,
                embedding_str,
                top_k
            )

        return [
            ChunkRecord(
                id=r["id"],
                document_id=r["document_id"],
                content=r["content"],
                metadata= r["metadata"],
            )
            for r in rows
        ]

    def _parse_embedding(self, embedding: list[float])-> str:
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        return embedding_str
        