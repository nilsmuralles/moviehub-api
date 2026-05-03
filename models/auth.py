from pydantic import BaseModel
from typing import Optional

class SignUpRequest(BaseModel):
    username: str
    password: str
    is_premium: Optional[bool] = False
    avatar_path: Optional[str] = None

class GenreSelectionRequest(BaseModel):
    userId: str
    genre_ids: list[str]

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    userId: str
    username: str
    is_premium: bool
    join_date: Optional[str] = None
    avatar_path: Optional[str] = None
