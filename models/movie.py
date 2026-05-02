from pydantic import BaseModel
from typing import Optional

class MovieBase(BaseModel):
    title: str
    release_date: Optional[str] = None
    overview: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    genres: Optional[list[str]] = None
    is_adult: Optional[bool] = False
    budget: Optional[int] = None
    homepage: Optional[str] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: Optional[str] = None


class MovieCreate(MovieBase):
    movieId: int

class MovieUpdate(MovieBase):
    title: Optional[str] = None

class Movie(MovieBase):
    movieId: int

    class Config:
        from_attributes = True
