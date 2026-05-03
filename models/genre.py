from pydantic import BaseModel
from typing import Optional

class GenreBase(BaseModel):
    name: str
    movie_count: Optional[int] = None
    avg_rating: Optional[float] = None
    popularity_score: Optional[float] = None
    is_classic: Optional[bool] = None

class GenreCreate(GenreBase):
    genreId: str

class GenreUpdate(GenreBase):
    name: Optional[str] = None

class Genre(GenreBase):
    genreId: str

    class Config:
        from_attributes = True
