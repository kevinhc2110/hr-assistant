from hr_assistant.infrastructure.vectorstore.models import ChunkRecord


class RetrieveContextUseCase:

    def __init__(
        self,
        embedding_provider,
        vector_store
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def execute(self, query: str, top_k: int = 5)-> list[ChunkRecord]:
        
        query_embedding = await self.embedding_provider.embed(query)

        results = await self.vector_store.search(
            embedding=query_embedding,
            top_k=top_k
        )

        return results
    
    
      