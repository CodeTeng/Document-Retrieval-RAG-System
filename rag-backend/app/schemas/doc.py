from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UploadResponse(BaseModel):
    status: str
    doc_id: str
    length: int
    message: Optional[str] = None

class DocItem(BaseModel):
    id: str
    name: str
    upload_time: str
    status: str
    size: Optional[int] = None
