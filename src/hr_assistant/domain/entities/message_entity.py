from dataclasses import dataclass


@dataclass
class Messages:
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str