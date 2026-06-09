from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

import pytest

from hr_assistant.domain.entities.conversation_entity import Conversation
from hr_assistant.domain.entities.message_entity import Messages
from hr_assistant.infrastructure.vectorstore.models import ChunkRecord


@pytest.fixture
def mock_chat_repository():
    repo = MagicMock()
    repo.save_conversation = AsyncMock()
    repo.save_message = AsyncMock()
    repo.get_conversations = AsyncMock()
    repo.get_messages = AsyncMock()
    return repo


@pytest.fixture
def mock_llm_provider():
    provider = MagicMock()
    provider.generate = AsyncMock(return_value="Esta es una respuesta de prueba.")
    return provider


@pytest.fixture
def mock_embedding_provider():
    provider = MagicMock()
    provider.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])
    provider.embed_batch = AsyncMock(
        return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    )
    return provider


@pytest.fixture
def mock_vector_store():
    store = MagicMock()
    store.add = AsyncMock()
    store.search = AsyncMock()
    return store


@pytest.fixture
def mock_retrieve_context_use_case():
    use_case = MagicMock()
    use_case.execute = AsyncMock(
        return_value=[
            ChunkRecord(
                id=str(uuid4()),
                document_id=str(uuid4()),
                content="Chunk de prueba 1",
            ),
            ChunkRecord(
                id=str(uuid4()),
                document_id=str(uuid4()),
                content="Chunk de prueba 2",
            ),
        ]
    )
    return use_case


@pytest.fixture
def mock_document_repository():
    repo = MagicMock()
    repo.save_document = AsyncMock()
    return repo


@pytest.fixture
def sample_conversation():
    return Conversation(
        id=str(uuid4()),
        user_id="00000000-0000-0000-0000-000000000000",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_message():
    return Messages(
        id=str(uuid4()),
        conversation_id=str(uuid4()),
        role="user",
        content="¿Cuál es la política de vacaciones?",
        created_at=datetime.now(timezone.utc),
    )
