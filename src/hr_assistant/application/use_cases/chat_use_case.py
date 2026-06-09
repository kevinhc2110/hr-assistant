from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import uuid4

from hr_assistant.domain.entities.conversation_entity import Conversation
from hr_assistant.domain.entities.message_entity import Messages


class ChatUseCase:

    def __init__(
        self,
        llm_provider,
        conversations_use_case,
        messages_use_case,
        retrieve_context_use_case,
    ):
        self.llm_provider = llm_provider
        self.conversations_use_case = conversations_use_case
        self.messages_use_case = messages_use_case
        self.retrieve_context_use_case = retrieve_context_use_case
        
    async def execute(
        self,
        question: str,
        conversation_id: str | None = None,
    ) -> dict:
        if conversation_id is None:
            conversation = await self.conversations_use_case.execute_create(
                user_id="00000000-0000-0000-0000-000000000000"
                )
            
            conversation_id = conversation.id

        history_messages = await self.messages_use_case.execute(
            conversation_id=conversation_id
        )
        
        await self.messages_use_case.execute_create(
            conversation_id=conversation_id,
            role="user",
            content=question
            )

        history_text = "\n\n".join(
            f"[{m['role']}] {m['content']}"
            for m in reversed(history_messages) 
        )

        context_chunks = await self.retrieve_context_use_case.execute(
            query=question,
            top_k=5
        )

        context_text = "\n\n".join(
            f"[Chunk {i+1}] {c.content}"
            for i, c in enumerate(context_chunks)
        )

        prompt = f"""
            Historial de conversación:
            {history_text}

            Contexto:

            {context_text}

            Pregunta:
            {question}
        """

        answer = await self.llm_provider.generate(prompt=prompt)

        await self.messages_use_case.execute_create(
            conversation_id=conversation_id,
            role="assistant",
            content=answer
            )

        return {
            "conversation_id": conversation_id,
            "answer": answer
        }
    
    async def execute_stream(
        self,
        question: str,
        conversation_id: str,
    ) -> AsyncGenerator[str, None]:

        history_messages = await self.messages_use_case.execute(
            conversation_id=conversation_id
        )

        await self.messages_use_case.execute_create(
            conversation_id=conversation_id,
            role="user",
            content=question
            )
        
        history_text = "\n\n".join(
            f"[{m['role']}] {m['content']}"
            for m in reversed(history_messages) 
        )

        context_chunks = await self.retrieve_context_use_case.execute(
            query=question,
            top_k=5
        )

        context_text = "\n\n".join(
            f"[Chunk {i+1}] {c.content}"
            for i, c in enumerate(context_chunks)
        )

        prompt = f"""
            Historial de conversación:
            {history_text}

            Contexto:

            {context_text}

            Pregunta:
            {question}
        """

        full_answer = ""

        try: 
            async for chunk in self.llm_provider.stream_generate(prompt=prompt):
                full_answer += chunk
                yield chunk

        finally:
            if full_answer:
                 await self.messages_use_case.execute_create(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=full_answer
                )
