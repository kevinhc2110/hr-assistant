from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi import Depends

from hr_assistant.api.schemas.chat_schema import ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from hr_assistant.application.use_cases.chat_use_case import ChatUseCase
from hr_assistant.application.use_cases.conversations_use_case import ConversationsUseCase
from hr_assistant.application.use_cases.messages_use_case import MessagesUseCase
from hr_assistant.core.dependencies import get_chat_use_case, get_conversations_use_case, get_messages_use_case

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

@router.get(
    "/conversations",
    response_model=list[ConversationResponse],
)
async def conversations(
    user_id: str = Query(...),
    use_case: ConversationsUseCase = Depends(
        get_conversations_use_case
    ),
):
    convs = await use_case.execute(user_id=user_id)

    return [
        ConversationResponse(
            id=c["id"],
            created_at=c["created_at"].isoformat(),
        )
        for c in convs
    ]


@router.get(
    "/messages",
    response_model=list[MessageResponse],
)
async def messages(
    conversation_id: str = Query(...),
    use_case: MessagesUseCase = Depends(
        get_messages_use_case
    ),
):
    msgs = await use_case.execute(conversation_id=conversation_id)

    return [
        MessageResponse(
            id=m["id"],
            role=m["role"],
            content=m["content"],
            created_at=m["created_at"].isoformat(),
        )
        for m in msgs
    ]

@router.post("/chat")
async def chat(
    request: ChatRequest,
    use_case_chat: ChatUseCase = Depends(get_chat_use_case),
):
    answer = await use_case_chat.execute(
        question=request.message,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        conversation_id=answer["conversation_id"],
        answer=answer["answer"],
    )

@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    use_case_chat: ChatUseCase = Depends(get_chat_use_case),
    use_case_conversations: ConversationsUseCase = Depends(get_conversations_use_case),
):
    await websocket.accept()

    existing = await use_case_conversations.execute(
        user_id="00000000-0000-0000-0000-000000000000",
    )

    if existing:
        conversation_id = existing[0]["id"]
    else:
        conversation = await use_case_conversations.execute_create(
            user_id="00000000-0000-0000-0000-000000000000",
        )
        conversation_id = conversation.id

    await websocket.send_json({
        "type": "conversation_created",
        "conversation_id": conversation_id,
    })

    try:
        while True:
            data = await websocket.receive_json()

            question = data.get("message", "").strip()

            if not question:
                await websocket.send_json({
                    "type": "error",
                    "message": "message is required"
                })
                continue

            async for chunk in use_case_chat.execute_stream(
                question=question,
                conversation_id=conversation_id,
            ):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })

            await websocket.send_json(
                {
                    "type": "done",
                }
            )

    except WebSocketDisconnect:
        pass


