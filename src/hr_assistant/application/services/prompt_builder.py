from hr_assistant.domain.models.chunk_record import ChunkRecord


class PromptBuilder:

    @staticmethod
    def build(
        question: str,
        history_text: str,
        context_chunks: list[ChunkRecord],
    ) -> str:
        context_text = "\n\n".join(
            f"[Chunk {i+1}] {c.content}"
            for i, c in enumerate(context_chunks)
        )

        return f"""
Historial de conversación:
{history_text}

Contexto:
{context_text}

Pregunta:
{question}
"""
