from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_driver
from models.recommendation import RecommendedMovie
from repository.recommendation import RecommendationRepository
from services.recommendation import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

def get_service() -> RecommendationService:
    driver = get_driver()
    repository = RecommendationRepository(driver)
    return RecommendationService(repository)

@router.get("/{user_id}", response_model=list[RecommendedMovie])
def get_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    service: RecommendationService = Depends(get_service),
):
    results = service.recommend(user_id, limit)
    if not results:
        raise HTTPException(status_code=404, detail="No recommendations found for this user")
    return results
