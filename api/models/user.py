from pydantic import BaseModel

class User(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    is_active: bool | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None