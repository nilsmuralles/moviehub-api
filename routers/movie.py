from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_driver
from models.movie import Movie, MovieCreate, MovieUpdate
from repository.movie import MovieRepository
from services.movie import MovieService

router = APIRouter(prefix="/movies", tags=["movies"])

def get_service() -> MovieService:
    driver = get_driver()
    repository = MovieRepository(driver)
    return MovieService(repository)

@router.get("/", response_model=list[Movie])
def get_all_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    service: MovieService = Depends(get_service),
):
    return service.get_all(skip=skip, limit=limit)

@router.get("/search", response_model=list[Movie])
def search_movies(
    title: str = Query(..., min_length=1),
    service: MovieService = Depends(get_service),
):
    return service.search_by_title(title)

@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: int, service: MovieService = Depends(get_service)):
    movie = service.get_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.post("/", response_model=Movie, status_code=201)
def create_movie(data: MovieCreate, service: MovieService = Depends(get_service)):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{movie_id}", response_model=Movie)
def update_movie(
    movie_id: int,
    data: MovieUpdate,
    service: MovieService = Depends(get_service),
):
    movie = service.update(movie_id, data)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, service: MovieService = Depends(get_service)):
    deleted = service.delete(movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Movie not found")
