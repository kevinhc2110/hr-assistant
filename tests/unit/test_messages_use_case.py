from uuid import uuid4
from datetime import datetime, timezone

import pytest

from hr_assistant.application.use_cases.messages_use_case import MessagesUseCase
from hr_assistant.domain.entities.message_entity import Messages


class TestMessagesUseCase:
    @pytest.fixture
    def use_case(self, mock_chat_repository):
        return MessagesUseCase(chat_repository=mock_chat_repository)

    async def test_execute_returns_messages_list(self, use_case, mock_chat_repository):
        conv_id = str(uuid4())
        now = datetime.now(timezone.utc)
        messages = [
            Messages(
                id=str(uuid4()),
                conversation_id=conv_id,
                role="user",
                content="Pregunta",
                created_at=now,
            ),
            Messages(
                id=str(uuid4()),
                conversation_id=conv_id,
                role="assistant",
                content="Respuesta",
                created_at=now,
            ),
        ]
        mock_chat_repository.get_messages.return_value = messages

        result = await use_case.execute(conversation_id=conv_id)

        assert len(result) == 2
        assert result[0]["id"] == messages[0].id
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"
        mock_chat_repository.get_messages.assert_awaited_once_with(
            conversation_id=conv_id,
        )

    async def test_execute_returns_empty_list(self, use_case, mock_chat_repository):
        mock_chat_repository.get_messages.return_value = []

        result = await use_case.execute(conversation_id=str(uuid4()))

        assert result == []
