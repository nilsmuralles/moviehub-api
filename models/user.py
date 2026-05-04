from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    is_premium: Optional[bool] = None
    avatar_path: Optional[str] = None

class UserCreate(UserBase):
    userId: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_premium: Optional[bool] = None
    avatar_path: Optional[str] = None

class User(UserBase):
    userId: str
    join_date: Optional[str] = None

    class Config:
        from_attributes = True

class GenreUpdate(BaseModel):
    genres: list[str]
