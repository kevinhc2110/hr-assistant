
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Conversation:
    id: str
    user_id: str
    created_at: datetime