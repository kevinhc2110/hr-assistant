from collections.abc import AsyncGenerator

from hr_assistant.infrastructure.llm.base import LLMProvider
from google import genai
from google.genai import types

HR_SYSTEM_PROMPT = """
    Eres un asistente de Recursos Humanos especializado en soporte interno de empresa.

    Tu función es:
    - Responder preguntas sobre políticas de la empresa
    - Explicar beneficios, vacaciones, licencias y normas laborales
    - Ayudar con procesos de onboarding y procedimientos internos
    - Resolver dudas frecuentes de empleados

    Reglas:
    - Responde de forma clara, profesional y directa
    - No inventes políticas; si no tienes información, dilo explícitamente
    - Prioriza respuestas cortas y accionables
    - Si la pregunta es ambigua, pide aclaración
    - No des asesoría legal, solo orientación general interna

    Estilo:
    - Tono profesional, amigable y neutral
    - Sin respuestas largas innecesarias
"""
class GeminiProvider(LLMProvider):
    
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model


    async def generate(self, prompt: str, system_instruction: str = HR_SYSTEM_PROMPT, temperature: float = 0.5) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction
            )
        )
        return response.text
    
    async def stream_generate(
        self,
        prompt: str,
        system_instruction: str = HR_SYSTEM_PROMPT,
        temperature: float = 0.5,
    ) -> AsyncGenerator[str, None]:

        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction
            )
        ):
        
            if chunk.text:
                yield chunk.text

        