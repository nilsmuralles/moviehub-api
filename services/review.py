from datetime import date
from models.review import Review, ReviewCreate, ReviewUpdate
from repository.review import ReviewRepository

class ReviewService:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    def create(self, data: ReviewCreate) -> Review:
        data.created_at = date.today()

        record = self.repository.create(data)
        return Review(**record)

    def update(self, review_id: int, data: ReviewUpdate) -> Review | None:
        data.updated_at = date.today()

        record = self.repository.update(review_id, data)
        return Review(**record) if record else None
    
    def get_all(self, skip: int = 0, limit: int = 25) -> list[Review]:
        records = self.repository.find_all(skip=skip, limit=limit)
        return [Review(**r) for r in records]

    def get_by_id(self, review_id: str) -> Review | None:
        record = self.repository.find_by_id(review_id)
        return Review(**record) if record else None

    def get_by_movie(self, movie_id: int) -> list[Review]:
        records = self.repository.find_by_movie(movie_id)
        return [Review(**r) for r in records]

    def delete(self, review_id: str) -> bool:
        return self.repository.delete(review_id)
