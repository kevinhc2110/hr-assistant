from hr_assistant.domain.entities.conversation_entity import Conversation
from hr_assistant.domain.entities.message_entity import Messages



class ChatRepository:
    def __init__(self, db):
        self.db =  db

    async def save_conversation(self, conversation: Conversation):
        await self.db.execute(
            """
            INSERT INTO conversations (
                id,
                user_id,
                created_at
            )
            VALUES ($1, $2, $3)
            """,
            conversation.id,
            conversation.user_id,
            conversation.created_at
        )

    async def save_message(self, chat: Messages):
        await self.db.execute(
            """
            INSERT INTO messages (
                id,
                conversation_id,
                role,
                content,
                created_at
            )
            VALUES ($1, $2, $3, $4, $5)
            """,
            chat.id,
            chat.conversation_id,
            chat.role,
            chat.content,
            chat.created_at
        )
        pass
    
    async def get_conversations(self, user_id: str, limit: int = 20):
        rows = await self.db.fetch(
            """
            SELECT
                id,
                user_id,
                created_at
            FROM conversations
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2;
            """,
            user_id,
            limit
        )

        return [Conversation(
            id=r["id"],
            user_id=r["user_id"],
            created_at=r["created_at"]
        ) for r in rows ]

    async def get_messages(self, conversation_id: str, limit: int = 20):
        rows = await self.db.fetch(
            """
            SELECT
                id,
                conversation_id,
                role,
                content,
                created_at
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at DESC
            LIMIT $2;
            """,
            conversation_id,
            limit
        )
        return [Messages(
            id=r["id"],
            conversation_id=r["conversation_id"],
            role=r["role"],
            content=r["content"],
            created_at=r["created_at"]
        ) for r in rows ]