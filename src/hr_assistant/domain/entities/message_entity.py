from dataclasses import dataclass
from datetime import datetime


@dataclass
class Messages:
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime