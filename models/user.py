from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    name: str
    password: str
    is_premium: bool
    join_date: date
    genres: Optional[list] = None
    avatar_path: Optional[str] = None

class UserCreate(UserBase):
    userId: int

class UserUpdate(UserBase):
    name: Optional[str] = None

class User(UserBase):
    userId: int

    class Config:
        from_attributes = True