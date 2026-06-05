class MessagesUseCase:

    def __init__(
        self,
        chat_repository,
    ):
        self.chat_repository = chat_repository

    async def execute(
        self,
        conversation_id: str,
    ) -> list[dict]:
        messages = await self.chat_repository.get_messages(
            conversation_id=conversation_id,
        )

        return [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at
            }
            for message in messages
        ]