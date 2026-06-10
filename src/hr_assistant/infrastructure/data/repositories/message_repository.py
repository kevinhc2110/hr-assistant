from hr_assistant.domain.entities.message_entity import Messages
from hr_assistant.domain.repositories.message_repository import (
    MessageRepository as MessageRepositoryInterface,
)


class MessageRepository(MessageRepositoryInterface):

    def __init__(self, db):
        self.db = db

    async def save(self, message: Messages) -> Messages:
        await self.db.execute(
            """
            INSERT INTO messages (id, conversation_id, role, content, created_at)
            VALUES ($1, $2, $3, $4, $5)
            """,
            message.id,
            message.conversation_id,
            message.role,
            message.content,
            message.created_at,
        )
        return message

    async def get_by_conversation(
        self, conversation_id: str, limit: int = 20
    ) -> list[Messages]:
        rows = await self.db.fetch(
            """
            SELECT id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            conversation_id,
            limit,
        )
        return [
            Messages(
                id=str(r["id"]),
                conversation_id=str(r["conversation_id"]),
                role=r["role"],
                content=r["content"],
                created_at=r["created_at"],
            )
            for r in rows
        ]
