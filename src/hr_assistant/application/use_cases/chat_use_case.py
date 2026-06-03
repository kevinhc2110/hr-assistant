from src.hr_assistant.infrastructure.llm.base import LLMProvider


class ChatUseCase:

    def __init__(
        self,
        llm_provider: LLMProvider
    ):
        self.llm_provider = llm_provider

    async def execute(
        self,
        question: str
    ):

        return await self.llm_provider.generate(
            prompt=question
        )