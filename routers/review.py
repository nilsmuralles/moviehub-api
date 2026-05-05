from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_driver
from models.review import Review, ReviewCreate, ReviewUpdate, ReviewBulkAction
from repository.review import ReviewRepository
from services.review import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])

def get_service() -> ReviewService:
    driver = get_driver()
    repository = ReviewRepository(driver)
    return ReviewService(repository)

@router.get("/", response_model=list[Review])
def get_all_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    service: ReviewService = Depends(get_service),
):
    return service.get_all(skip=skip, limit=limit)

@router.get("/search", response_model=list[Review])
def search_reviews(
    movie_id: int = Query(...),
    service: ReviewService = Depends(get_service),
):
    return service.get_by_movie(movie_id)

@router.get("/{review_id}", response_model=Review)
def get_review(review_id: str, service: ReviewService = Depends(get_service)):
    review = service.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.post("/", response_model=Review, status_code=201)
def create_review(data: ReviewCreate, service: ReviewService = Depends(get_service)):
    return service.create(data)

@router.patch("/{review_id}", response_model=Review)
def update_review(
    review_id: str,
    data: ReviewUpdate,
    service: ReviewService = Depends(get_service),
):
    review = service.update(review_id, data)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, service: ReviewService = Depends(get_service)):
    deleted = service.delete(review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    
@router.delete("/bulk")
def delete_reviews(data: ReviewBulkAction, service: ReviewService = Depends(get_service)):
    service.delete_reviews(data.reviewIds)
    return {"message": "Reviews deleted"}

@router.put("/reviews/hide")
def hide_reviews(data: ReviewBulkAction, service: ReviewService = Depends(get_service)):
    service.hide_reviews(data.reviewIds)
    return {"message": "Reviews hidden"}

@router.get("/movie/{movie_id}", response_model=list[Review])
def get_reviews_by_movie(movie_id: int, service: ReviewService = Depends(get_service)):
    reviews = service.get_by_movie(movie_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this movie")
    return reviews
