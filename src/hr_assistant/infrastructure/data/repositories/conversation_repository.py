from hr_assistant.domain.entities.conversation_entity import Conversation
from hr_assistant.domain.repositories.conversation_repository import (
    ConversationRepository as ConversationRepositoryInterface,
)


class ConversationRepository(ConversationRepositoryInterface):

    def __init__(self, db):
        self.db = db

    async def save(self, conversation: Conversation) -> Conversation:
        await self.db.execute(
            """
            INSERT INTO conversations (id, user_id, created_at)
            VALUES ($1, $2, $3)
            """,
            conversation.id,
            conversation.user_id,
            conversation.created_at,
        )
        return conversation

    async def get_by_user(self, user_id: str, limit: int = 20) -> list[Conversation]:
        rows = await self.db.fetch(
            """
            SELECT id, user_id, created_at
            FROM conversations
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            user_id,
            limit,
        )
        return [
            Conversation(
                id=str(r["id"]),
                user_id=str(r["user_id"]),
                created_at=r["created_at"],
            )
            for r in rows
        ]
