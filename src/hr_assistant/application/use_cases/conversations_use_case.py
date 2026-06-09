from datetime import datetime, timezone
from uuid import uuid4

from hr_assistant.domain.entities.conversation_entity import Conversation


class ConversationsUseCase:

    def __init__(
        self,
        chat_repository,
    ):
        self.chat_repository = chat_repository

    async def execute(
        self,
        user_id: str,
    ) -> list[dict]:
        conversations = await self.chat_repository.get_conversations(
            user_id=user_id,
        )

        return [
            {
                "id": conversation.id,
                "created_at": conversation.created_at
            }
            for conversation in conversations
        ]
    
    async def execute_create(
        self,
        user_id: str,
    ) -> Conversation:
        
        conversation = await self.chat_repository.save_conversation(
            Conversation(
                id=str(uuid4()),
                user_id=user_id,
                created_at=datetime.now(timezone.utc)
            )
        )       
        return conversation