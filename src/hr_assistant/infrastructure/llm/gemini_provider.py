from src.hr_assistant.infrastructure.llm.base import LLMProvider
from google import genai
from google.genai import types


class GeminiProvider(LLMProvider):

    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str, system_instruction: str | None = None, temperature: float = 0.3) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction
            )
        )
        return response.text