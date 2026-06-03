from pydantic import BaseModel

class UploadDocumentResponse(BaseModel):
    filename: str