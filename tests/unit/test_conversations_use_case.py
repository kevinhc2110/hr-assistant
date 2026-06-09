from uuid import uuid4
from datetime import datetime, timezone

import pytest

from hr_assistant.application.use_cases.conversations_use_case import ConversationsUseCase
from hr_assistant.domain.entities.conversation_entity import Conversation


class TestConversationsUseCase:
    @pytest.fixture
    def use_case(self, mock_chat_repository):
        return ConversationsUseCase(chat_repository=mock_chat_repository)

    async def test_execute_returns_conversations_list(self, use_case, mock_chat_repository):
        now = datetime.now(timezone.utc)
        conversations = [
            Conversation(id=str(uuid4()), user_id="user-1", created_at=now),
            Conversation(id=str(uuid4()), user_id="user-1", created_at=now),
        ]
        mock_chat_repository.get_conversations.return_value = conversations

        result = await use_case.execute(user_id="user-1")

        assert len(result) == 2
        assert result[0]["id"] == conversations[0].id
        assert result[0]["created_at"] == now
        mock_chat_repository.get_conversations.assert_awaited_once_with(
            user_id="user-1",
        )

    async def test_execute_returns_empty_list(self, use_case, mock_chat_repository):
        mock_chat_repository.get_conversations.return_value = []

        result = await use_case.execute(user_id="user-unknown")

        assert result == []
