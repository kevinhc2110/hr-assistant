from pydantic import BaseModel

class UploadDocumentResponse(BaseModel):
    id: str
    filename: str

