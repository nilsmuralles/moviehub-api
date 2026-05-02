from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReviewBase(BaseModel):
    rating: int
    content: Optional[str] = None
    url: Optional[str] = None


class ReviewCreate(ReviewBase):
    reviewId: int
    userId: int
    movieId: int


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    content: Optional[str] = None
    url: Optional[str] = None


class Review(ReviewBase):
    reviewId: int
    userId: int
    movieId: int
    created_at: date
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True