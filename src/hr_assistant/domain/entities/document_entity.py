from dataclasses import dataclass


@dataclass
class Document:
    id: str
    filename: str
    created_at: str
        