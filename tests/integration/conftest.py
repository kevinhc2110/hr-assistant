from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hr_assistant.api.routers.chat_router import router as chat_router
from hr_assistant.api.routers.documents_router import router as document_router
from hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from hr_assistant.application.use_cases.conversations_use_case import ConversationsUseCase
from hr_assistant.application.use_cases.messages_use_case import MessagesUseCase
from hr_assistant.application.use_cases.ingest_document_use_case import IngestDocumentUseCase
from hr_assistant.domain.entities.conversation_entity import Conversation
from hr_assistant.infrastructure.vectorstore.models import ChunkRecord
from hr_assistant.core.dependencies import (
    get_chat_use_case,
    get_conversations_use_case,
    get_messages_use_case,
    get_ingest_document_use_case,
)


@pytest.fixture
def app():
    application = FastAPI()
    application.include_router(chat_router)
    application.include_router(document_router)
    return application


FIXED_CONVERSATION_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def mock_chat_use_case():
    use_case = MagicMock(spec=ChatUseCase)

    async def execute_side_effect(question, conversation_id=None):
        return {
            "conversation_id": conversation_id or FIXED_CONVERSATION_ID,
            "answer": "Respuesta simulada del asistente.",
        }

    use_case.execute = AsyncMock(side_effect=execute_side_effect)

    async def stream_side_effect(question, conversation_id):
        yield "Respuesta"
        yield " simulada"
        yield " del asistente."

    use_case.execute_stream = stream_side_effect
    return use_case


@pytest.fixture
def mock_conversations_use_case():
    use_case = MagicMock(spec=ConversationsUseCase)
    use_case.execute = AsyncMock(
        return_value=[
            {"id": str(uuid4()), "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc)},
        ]
    )
    use_case.execute_create = AsyncMock(
        return_value=Conversation(
            id=FIXED_CONVERSATION_ID,
            user_id="00000000-0000-0000-0000-000000000000",
            created_at=datetime.now(timezone.utc),
        )
    )
    return use_case


@pytest.fixture
def mock_messages_use_case():
    use_case = MagicMock(spec=MessagesUseCase)
    use_case.execute = AsyncMock(
        return_value=[
            {
                "id": str(uuid4()),
                "role": "user",
                "content": "Hola",
                "created_at": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            },
            {
                "id": str(uuid4()),
                "role": "assistant",
                "content": "¿En qué puedo ayudarte?",
                "created_at": datetime(2024, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
            },
        ]
    )
    return use_case


@pytest.fixture
def mock_ingest_document_use_case():
    use_case = MagicMock(spec=IngestDocumentUseCase)
    use_case.execute = AsyncMock(
        return_value={
            "id": str(uuid4()),
            "filename": "test.txt",
        }
    )
    return use_case


@pytest.fixture
def client(app, mock_chat_use_case, mock_conversations_use_case, mock_messages_use_case, mock_ingest_document_use_case):
    app.dependency_overrides[get_chat_use_case] = lambda: mock_chat_use_case
    app.dependency_overrides[get_conversations_use_case] = lambda: mock_conversations_use_case
    app.dependency_overrides[get_messages_use_case] = lambda: mock_messages_use_case
    app.dependency_overrides[get_ingest_document_use_case] = lambda: mock_ingest_document_use_case

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
