from uuid import uuid4

import pytest

from hr_assistant.application.use_cases.retrieve_context_use_case import RetrieveContextUseCase
from hr_assistant.infrastructure.vectorstore.models import ChunkRecord


class TestRetrieveContextUseCase:
    @pytest.fixture
    def use_case(self, mock_embedding_provider, mock_vector_store):
        return RetrieveContextUseCase(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

    async def test_execute_returns_chunks(self, use_case, mock_embedding_provider, mock_vector_store):
        expected_chunks = [
            ChunkRecord(
                id=str(uuid4()),
                document_id=str(uuid4()),
                content="Chunk relevante 1",
            ),
            ChunkRecord(
                id=str(uuid4()),
                document_id=str(uuid4()),
                content="Chunk relevante 2",
            ),
        ]
        mock_vector_store.search.return_value = expected_chunks

        result = await use_case.execute(query="política de vacaciones", top_k=3)

        assert len(result) == 2
        assert result == expected_chunks
        mock_embedding_provider.embed.assert_awaited_once_with(
            "política de vacaciones",
        )
        mock_vector_store.search.assert_awaited_once_with(
            embedding=[0.1, 0.2, 0.3],
            top_k=3,
        )

    async def test_execute_with_default_top_k(self, use_case, mock_embedding_provider, mock_vector_store):
        mock_vector_store.search.return_value = []

        result = await use_case.execute(query="test")

        assert result == []
        mock_vector_store.search.assert_awaited_once_with(
            embedding=[0.1, 0.2, 0.3],
            top_k=5,
        )
