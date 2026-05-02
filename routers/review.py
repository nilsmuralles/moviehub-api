from fastapi import APIRouter, Depends, HTTPException
from models.review import Review, ReviewCreate, ReviewUpdate
from services.review import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=Review, status_code=201)
def create_review(data: ReviewCreate, service: ReviewService = Depends()):
    return service.create(data)


@router.patch("/{review_id}", response_model=Review)
def update_review(
    review_id: int,
    data: ReviewUpdate,
    service: ReviewService = Depends()
):
    review = service.update(review_id, data)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review