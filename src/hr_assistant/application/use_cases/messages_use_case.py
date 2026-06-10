from datetime import datetime, timezone
from uuid import uuid4

from hr_assistant.domain.entities.message_entity import Messages


class MessagesUseCase:

    def __init__(
        self,
        message_repository,
    ):
        self.message_repository = message_repository

    async def execute(
        self,
        conversation_id: str,
    ) -> list[dict]:
        messages = await self.message_repository.get_by_conversation(
            conversation_id=conversation_id,
        )

        return [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ]

    async def execute_create(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> Messages:
        message = await self.message_repository.save(
            Messages(
                id=str(uuid4()),
                conversation_id=conversation_id,
                role=role,
                content=content,
                created_at=datetime.now(timezone.utc),
            )
        )

        return message