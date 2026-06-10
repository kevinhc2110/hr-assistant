from abc import ABC, abstractmethod

from hr_assistant.domain.entities.message_entity import Messages


class MessageRepository(ABC):

    @abstractmethod
    async def save(self, message: Messages) -> Messages:
        pass

    @abstractmethod
    async def get_by_conversation(self, conversation_id: str, limit: int = 20) -> list[Messages]:
        pass
