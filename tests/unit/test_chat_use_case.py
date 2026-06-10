from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

from hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from hr_assistant.infrastructure.constants import ANONYMOUS_USER_ID


class TestChatUseCase:
    @pytest.fixture
    def use_case(self, mock_llm_provider, mock_conversations_use_case, mock_messages_use_case, mock_retrieve_context_use_case):
        return ChatUseCase(
            llm_provider=mock_llm_provider,
            conversations_use_case=mock_conversations_use_case,
            messages_use_case=mock_messages_use_case,
            retrieve_context_use_case=mock_retrieve_context_use_case,
        )

    async def test_execute_creates_new_conversation(self, use_case, mock_llm_provider, mock_conversations_use_case, mock_messages_use_case, mock_retrieve_context_use_case):
        result = await use_case.execute(question="¿Cuál es la política de vacaciones?")

        assert "conversation_id" in result
        assert result["answer"] == "Esta es una respuesta de prueba."

        mock_conversations_use_case.execute_create.assert_awaited_once_with(
            user_id=ANONYMOUS_USER_ID,
        )
        assert mock_messages_use_case.execute.await_count == 1
        assert mock_messages_use_case.execute_create.await_count == 2
        mock_llm_provider.generate.assert_awaited_once()
        mock_retrieve_context_use_case.execute.assert_awaited_once()

    async def test_execute_reuses_existing_conversation(self, use_case, mock_conversations_use_case, mock_messages_use_case):
        conv_id = str(uuid4())

        result = await use_case.execute(
            question="¿Cómo solicito vacaciones?",
            conversation_id=conv_id,
        )

        assert result["conversation_id"] == conv_id
        mock_conversations_use_case.execute_create.assert_not_awaited()
        assert mock_messages_use_case.execute.await_count == 1
        assert mock_messages_use_case.execute_create.await_count == 2

    async def test_execute_retrieves_context_and_generates_answer(self, use_case, mock_llm_provider, mock_retrieve_context_use_case):
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

    async def test_execute_handles_no_history(self, use_case, mock_llm_provider, mock_messages_use_case):
        mock_messages_use_case.execute.return_value = []

        result = await use_case.execute(question="Hola")

        assert result["answer"] == "Esta es una respuesta de prueba."
        mock_messages_use_case.execute_create.assert_awaited()

    async def test_execute_stream_yields_chunks(self, use_case, mock_llm_provider):
        async def stream_generator(prompt, system_instruction=None, temperature=0.5):
            yield "Chunk "
            yield "de "
            yield "prueba."

        mock_llm_provider.stream_generate = stream_generator

        chunks = []
        async for chunk in use_case.execute_stream(
            question="¿Cómo solicito vacaciones?",
            conversation_id=str(uuid4()),
        ):
            chunks.append(chunk)

        assert chunks == ["Chunk ", "de ", "prueba."]
