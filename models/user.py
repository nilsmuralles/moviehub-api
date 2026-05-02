from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    name: str
    is_premium: bool
    genres: Optional[list[str]] = None
    avatar_path: Optional[str] = None

class UserCreate(UserBase):
    userId: int
    password: str

class UserUpdate(UserBase):
    name: Optional[str] = None
    password: Optional[str] = None
    is_premium: Optional[bool] = None
    genres: Optional[list[str]] = None
    avatar_path: Optional[str] = None

class User(UserBase):
    userId: int
    join_date: date

    class Config:
        from_attributes = True