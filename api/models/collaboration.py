from pydantic import BaseModel

class CursorPosition(BaseModel):
    user_id: int
    position: int
    file_id: int

class Highlight(BaseModel):
    user_id: int
    start: int
    end: int
    file_id: int

class TextChange(BaseModel):
    user_id: int
    start: int
    delete_count: int
    insert: str
    file_id: int