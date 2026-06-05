
from fastapi import Depends, Request

from src.hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from src.hr_assistant.application.use_cases.ingest_document_use_case import IngestDocumentUseCase
from src.hr_assistant.application.use_cases.retrieve_context_use_case import RetrieveContextUseCase
from src.hr_assistant.infrastructure.embeddings.gemini_embeddings import GeminiEmbeddings
from src.hr_assistant.infrastructure.llm.gemini_provider import GeminiProvider
from src.hr_assistant.core.config import settings
from src.hr_assistant.infrastructure.repositories.document_repository import DocumentRepository
from src.hr_assistant.infrastructure.vectorstore.pgvector_store import PGVectorStore


llm_provider = GeminiProvider(
    api_key=settings.gemini_api_key,
    model=settings.gemini_model,
)

def get_llm_provider():
    return llm_provider
    
def get_database(request: Request):
    return request.app.state.db


def get_document_repository(db=Depends(get_database)):
    return DocumentRepository(db=db)

embedding_provider = GeminiEmbeddings(
    api_key=settings.gemini_api_key,
    model=settings.gemini_embedding_model,
)

def get_embedding_provider():
    return embedding_provider

def get_vector_store(db=Depends(get_database)):
    return PGVectorStore(db=db)

def get_ingest_document_use_case(
    document_repository = Depends(get_document_repository),
    embedding_provider = Depends(get_embedding_provider),
    vector_store = Depends(get_vector_store),
):
    return IngestDocumentUseCase(
        document_repository=document_repository,
        embedding_provider=embedding_provider,
        vector_store=vector_store
    )

def get_retrieve_context_use_case(
    embedding_provider = Depends(get_embedding_provider),
    vector_store = Depends(get_vector_store),
):
    return RetrieveContextUseCase(
        embedding_provider=embedding_provider,
        vector_store=vector_store
    )

def get_chat_use_case(
    llm_provider=Depends(get_llm_provider),
    retrieve_context_use_case=Depends(get_retrieve_context_use_case),
) -> ChatUseCase:

    return ChatUseCase(
        llm_provider=llm_provider,
        retrieve_context_use_case=retrieve_context_use_case
    )