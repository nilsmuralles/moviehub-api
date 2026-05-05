from fastapi import APIRouter, Depends, HTTPException
from database import get_driver
from repository.analytics import AnalyticsRepository
from services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_service() -> AnalyticsService:
    driver = get_driver()
    repository = AnalyticsRepository(driver)
    return AnalyticsService(repository)

@router.get("/movies/financials")
def movie_financials(service: AnalyticsService = Depends(get_service)):
    return service.get_movie_financials()

@router.get("/movies/financials/{movie_id}")
def movie_financials_by_id(movie_id: int, service: AnalyticsService = Depends(get_service)):
    result = service.get_movie_financials_by_id(movie_id)
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found or has no financial data")
    return result

@router.get("/movies/by-status")
def movies_by_status(service: AnalyticsService = Depends(get_service)):
    return service.get_movies_by_status()


@router.get("/movies/by-genre")
def movies_by_genre(service: AnalyticsService = Depends(get_service)):
    return service.get_movies_by_genre()

@router.get("/movies/release-date-range")
def release_date_range(service: AnalyticsService = Depends(get_service)):
    return service.get_release_date_range()

@router.get("/movies/top-rated")
def top_rated_movies(service: AnalyticsService = Depends(get_service)):
    return service.get_top_movies_by_rating()

@router.get("/users/genres")
def user_genres(service: AnalyticsService = Depends(get_service)):
    return service.get_user_genres()

@router.get("/companies/movie-count")
def movies_per_company(service: AnalyticsService = Depends(get_service)):
    return service.get_movies_per_company()

@router.get("/movies/genre/{genre}")
def movies_by_genre_name(genre: str, service: AnalyticsService = Depends(get_service)):
    results = service.get_movies_by_genre_name(genre)
    if not results:
        raise HTTPException(status_code=404, detail=f"No movies found for genre '{genre}'")
    return results
