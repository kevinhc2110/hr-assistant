from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    id: str
    filename: str
    created_at: datetime
        