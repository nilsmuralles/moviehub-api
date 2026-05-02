from pydantic import BaseModel
from typing import Optional

class PersonBase(BaseModel):
    name: str
    known_for_department: Optional[str] = None
    popularity: Optional[float] = None
    gender: Optional[int] = None
    profile_path: Optional[str] = None

class PersonCreate(PersonBase):
    personId: int

class PersonUpdate(PersonBase):
    name: Optional[str] = None

class Person(PersonBase):
    personId: int

    class Config:
        from_attributes = True
