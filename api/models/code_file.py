from pydantic import BaseModel
from datetime import datetime

class CodeFile(BaseModel):
    id: int
    filename: str
    content: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CodeFileCreate(BaseModel):
    filename: str

class CodeFileUpdate(BaseModel):
    content: str | None = None
    filename: str | None = None