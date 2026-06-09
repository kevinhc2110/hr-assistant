from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from hr_assistant.domain.entities.message_entity import Messages
from hr_assistant.infrastructure.vectorstore.models import ChunkRecord


class TestChatUseCase:
    @pytest.fixture
    def use_case(self, mock_chat_repository, mock_llm_provider, mock_retrieve_context_use_case):
        return ChatUseCase(
            chat_repository=mock_chat_repository,
            llm_provider=mock_llm_provider,
            retrieve_context_use_case=mock_retrieve_context_use_case,
        )

    @pytest.fixture
    def history_messages(self):
        return [
            Messages(
                id=str(uuid4()),
                conversation_id=str(uuid4()),
                role="user",
                content="Pregunta anterior",
                created_at="2024-01-01T00:00:00+00:00",
            ),
            Messages(
                id=str(uuid4()),
                conversation_id=str(uuid4()),
                role="assistant",
                content="Respuesta anterior",
                created_at="2024-01-01T00:00:05+00:00",
            ),
        ]

    async def test_execute_creates_new_conversation(self, use_case, mock_chat_repository, mock_llm_provider, mock_retrieve_context_use_case, history_messages):
        mock_chat_repository.get_messages.return_value = history_messages

        result = await use_case.execute(question="¿Cuál es la política de vacaciones?")

        assert "conversation_id" in result
        assert result["answer"] == "Esta es una respuesta de prueba."

        mock_chat_repository.save_conversation.assert_awaited_once()
        assert mock_chat_repository.save_message.await_count == 2
        mock_llm_provider.generate.assert_awaited_once()
        mock_retrieve_context_use_case.execute.assert_awaited_once()

    async def test_execute_reuses_existing_conversation(self, use_case, mock_chat_repository, mock_llm_provider, mock_retrieve_context_use_case, history_messages):
        conv_id = str(uuid4())
        mock_chat_repository.get_messages.return_value = history_messages

        result = await use_case.execute(
            question="¿Cómo solicito vacaciones?",
            conversation_id=conv_id,
        )

        assert result["conversation_id"] == conv_id
        mock_chat_repository.save_conversation.assert_not_awaited()
        assert mock_chat_repository.save_message.await_count == 2

    async def test_execute_retrieves_context_and_generates_answer(self, use_case, mock_chat_repository, mock_llm_provider, mock_retrieve_context_use_case, history_messages):
        mock_chat_repository.get_messages.return_value = history_messages

        result = await use_case.execute(question="¿Qué dice la política de home office?")

        mock_retrieve_context_use_case.execute.assert_awaited_once_with(
            query="¿Qué dice la política de home office?",
            top_k=5,
        )
        mock_llm_provider.generate.assert_awaited_once()
        prompt_arg = mock_llm_provider.generate.await_args.kwargs["prompt"]
        assert "¿Qué dice la política de home office?" in prompt_arg
        assert "Chunk de prueba" in prompt_arg
        assert result["answer"] == "Esta es una respuesta de prueba."

    async def test_execute_handles_no_history(self, use_case, mock_chat_repository, mock_llm_provider, mock_retrieve_context_use_case):
        mock_chat_repository.get_messages.return_value = []

        result = await use_case.execute(question="Hola")

        assert result["answer"] == "Esta es una respuesta de prueba."
        mock_chat_repository.save_message.assert_awaited()
