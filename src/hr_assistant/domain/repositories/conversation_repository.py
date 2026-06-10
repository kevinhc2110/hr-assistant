from abc import ABC, abstractmethod

from hr_assistant.domain.entities.conversation_entity import Conversation


class ConversationRepository(ABC):

    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation:
        pass

    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 20) -> list[Conversation]:
        pass
