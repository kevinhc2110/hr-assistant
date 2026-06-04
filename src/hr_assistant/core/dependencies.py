
from fastapi import Depends

from src.hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from src.hr_assistant.application.use_cases.ingest_document_use_case import IngestDocumentUseCase
from src.hr_assistant.application.use_cases.retrieve_context_use_case import RetrieveContextUseCase
from src.hr_assistant.infrastructure.database.postgres import PostgresDatabase
from src.hr_assistant.infrastructure.embeddings.gemini_embeddings import GeminiEmbeddings
from src.hr_assistant.infrastructure.llm.gemini_provider import GeminiProvider
from src.hr_assistant.core.config import settings
from src.hr_assistant.infrastructure.repositories.document_repository import DocumentRepository
from src.hr_assistant.infrastructure.vectorstore.pgvector_store import PGVectorStore


def get_llm_provider():

    return GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )

database = PostgresDatabase(
    dsn=settings.postgres_dsn
)

def get_database():
    return database


def get_document_repository():
    return DocumentRepository(db=get_database())

def get_embedding_provider():

    return GeminiEmbeddings(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )

vector_store = PGVectorStore(
    pool=None
)

def get_vector_store():
    return vector_store

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