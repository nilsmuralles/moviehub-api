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