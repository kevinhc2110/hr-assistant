
from dataclasses import dataclass


@dataclass
class Conversation:
    id: str
    user_id: str
    created_at: str