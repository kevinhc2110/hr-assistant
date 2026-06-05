from pydantic import BaseModel


class ChatRequest(BaseModel):
    coversation_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str

class CoversationRequest(BaseModel):
    user_id: str

class ConversationResponse(BaseModel):
    id: str
    created_at: str

class MessageRequest(BaseModel):
    conversation_id: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str