
from fastapi import Depends

from src.hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from src.hr_assistant.application.use_cases.ingest_document_use_case import IngestDocumentUseCase
from src.hr_assistant.infrastructure.embeddings.gemini_embeddings import GeminiEmbeddings
from src.hr_assistant.infrastructure.llm.gemini_provider import GeminiProvider
from src.hr_assistant.core.config import settings
from src.hr_assistant.infrastructure.repositories.document_repository import DocumentRepository


def get_llm_provider():

    return GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )

def get_chat_use_case(
    llm_provider=Depends(get_llm_provider),
) -> ChatUseCase:

    return ChatUseCase(
        llm_provider=llm_provider
    )

def get_document_repository():
    return DocumentRepository()

def get_ingest_document_use_case(
    repository=Depends(
        get_document_repository
    )
):
    return IngestDocumentUseCase(
        repository
    )

def get_embedding_provider():

    return GeminiEmbeddings(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )