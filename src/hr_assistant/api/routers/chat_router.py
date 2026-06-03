from fastapi import APIRouter
from fastapi import Depends

from src.hr_assistant.api.schemas.chat_schema import ChatRequest, ChatResponse
from src.hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from src.hr_assistant.core.dependencies import get_chat_use_case, get_embedding_provider

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    use_case: ChatUseCase = Depends(
        get_chat_use_case
    ),
):

    answer = await use_case.execute(
        question=request.message
    )

    return ChatResponse(
        answer=answer
    )

@router.get("/test-embedding")
async def test_embedding(
    embedding_provider = Depends(
        get_embedding_provider
    )
):

    embedding = await embedding_provider.embed(
        "Vacaciones"
    )

    return {
        "dimensions": len(embedding)
    }