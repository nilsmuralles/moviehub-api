from pydantic import BaseModel
from typing import Optional

class RecommendedMovie(BaseModel):
    movieId: int
    title: str
    vote_average: Optional[float] = None
    collaborative_score: float
    structural_score: float
    final_score: float
    reason: str
