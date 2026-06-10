from datetime import datetime, timezone
from uuid import uuid4

from hr_assistant.domain.entities.conversation_entity import Conversation


class ConversationsUseCase:

    def __init__(
        self,
        conversation_repository,
    ):
        self.conversation_repository = conversation_repository

    async def execute(
        self,
        user_id: str,
    ) -> list[dict]:
        conversations = await self.conversation_repository.get_by_user(
            user_id=user_id,
        )

        return [
            {
                "id": conversation.id,
                "created_at": conversation.created_at,
            }
            for conversation in conversations
        ]

    async def execute_create(
        self,
        user_id: str,
    ) -> Conversation:
        conversation = await self.conversation_repository.save(
            Conversation(
                id=str(uuid4()),
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
            )
        )
        return conversation