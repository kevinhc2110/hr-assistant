from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi import Depends

from src.hr_assistant.api.schemas.chat_schema import ChatRequest, ChatResponse, ConversationResponse, CoversationRequest, MessageRequest, MessageResponse
from src.hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from src.hr_assistant.application.use_cases.conversations_use_case import ConversationsUseCase
from src.hr_assistant.application.use_cases.messages_use_case import MessagesUseCase
from src.hr_assistant.core.dependencies import get_chat_use_case, get_conversations_use_case, get_messages_use_case

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

@router.get(
    "/conversations",
    response_model=list[ConversationResponse],
)
async def conversations(
    request: CoversationRequest,
    use_case: ConversationsUseCase = Depends(
        get_conversations_use_case
    ),
):
    conversations = await use_case.execute(
        user_id=request.user_id,
    )

    return [
        ConversationResponse(
            id=conversation["id"],
            created_at=conversation["created_at"].isoformat(),
        )
        for conversation in conversations
    ]


@router.get(
    "/messages",
    response_model=list[MessageResponse],
)
async def messages(
    request: MessageRequest,
    use_case: MessagesUseCase = Depends(
        get_messages_use_case
    ),
):
    messages = await use_case.execute(
        conversation_id=request.conversation_id,
    )

    return [
        MessageResponse(
            id=message["id"],
            role=message["role"],
            content=message["content"],
            created_at=message["created_at"].isoformat(),
        )
        for message in messages
    ]

@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    use_case: ChatUseCase = Depends(get_chat_use_case),
):
    await websocket.accept()

    conversation_id = None

    try:
        while True:
            data = await websocket.receive_json()
            # Espera: {"message": "...", "conversation_id": "..." (opcional)}

            question = data.get("message", "").strip()
            conversation_id = data.get("conversation_id") or conversation_id

            if not question:
                await websocket.send_json({"error": "message is required"})
                continue

            answer = await use_case.execute(
                question=question,
                conversation_id=conversation_id,
            )

            conversation_id = answer["conversation_id"]

            await websocket.send_json({
                "answer": answer["answer"],
                "conversation_id": conversation_id,
            })

    except WebSocketDisconnect:
        pass


# @router.post(
#     "",
#     response_model=ChatResponse,
# )
# async def chat(
#     request: ChatRequest,
#     use_case: ChatUseCase = Depends(
#         get_chat_use_case 
#     ),
# ):

#     answer = await use_case.execute(
#         user_id=request.coversation_id,
#         question=request.message
#     )

#     return ChatResponse(
#         answer=answer["answer"],
#         conversation_id=answer["conversation_id"]
#     )