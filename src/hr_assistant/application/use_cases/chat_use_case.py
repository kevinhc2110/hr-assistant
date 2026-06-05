from datetime import datetime, timezone
from uuid import uuid4

from src.hr_assistant.domain.entities.conversation_entity import Conversation
from src.hr_assistant.domain.entities.message_entity import Messages


class ChatUseCase:

    def __init__(
        self,
        chat_repository,
        llm_provider,
        retrieve_context_use_case,
    ):
        self.chat_repository = chat_repository
        self.llm_provider = llm_provider
        self.retrieve_context_use_case = retrieve_context_use_case

    async def execute(
        self,
        question: str,
        conversation_id: str | None = None,
    ) -> dict:
        if conversation_id is None:
            conversation = Conversation(
                id=str(uuid4()),
                user_id="00000000-0000-0000-0000-000000000000",
                created_at=datetime.now(timezone.utc),
            )
            await self.chat_repository.save_conversation(conversation)
            conversation_id = conversation.id

        await self.chat_repository.save_message(
            chat=Messages(
                id=str(uuid4()),
                conversation_id=conversation_id,
                role="user",
                content=question,
                created_at=datetime.now(timezone.utc)
            )
        )
        
        history_messages = await self.chat_repository.get_messages(
            conversation_id=conversation_id,
        )

        history_text = "\n\n".join(
            f"[{m.role}] {m.content}"
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

        await self.chat_repository.save_message(Messages(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            created_at=datetime.now(timezone.utc),
        ))

        return {
            "conversation_id": conversation_id,
            "answer": answer
        }