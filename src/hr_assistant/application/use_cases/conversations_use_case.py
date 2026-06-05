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