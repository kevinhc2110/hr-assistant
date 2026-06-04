from src.hr_assistant.infrastructure.llm.base import LLMProvider


class ChatUseCase:

    def __init__(
        self,
        llm_provider,
        retrieve_context_use_case
    ):
        self.llm_provider = llm_provider
        self.retrieve_context_use_case = retrieve_context_use_case

    async def execute(
        self,
        question: str
    ):
        context_chunks = await self.retrieve_context_use_case.execute(
            query=question,
            top_k=5
        )

        context = "\n\n".join(
            f"[Chunk {i+1}] {c.content}"
            for i, c in enumerate(context_chunks)
        )

        prompt = f"""
            Usa el siguiente contexto para responder:

            {context}

            Pregunta:
            {question}
        """

        return await self.llm_provider.generate(
            prompt=prompt
        )