from pydantic import BaseModel
from typing import Optional

class ReviewBase(BaseModel):
    rating: Optional[float] = None
    content: Optional[str] = None
    url: Optional[str] = None

class ReviewCreate(ReviewBase):
    reviewId: str
    userId: str
    movieId: int

class ReviewUpdate(BaseModel):
    rating: Optional[float] = None
    content: Optional[str] = None
    url: Optional[str] = None
    updated_at: Optional[str] = None

class Review(ReviewBase):
    reviewId: str
    userId: Optional[str] = None
    movieId: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
