from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_driver
from models.genre import Genre, GenreCreate, GenreUpdate
from repository.genre import GenreRepository
from services.genre import GenreService

router = APIRouter(prefix="/genres", tags=["genres"])

def get_service() -> GenreService:
    driver = get_driver()
    repository = GenreRepository(driver)
    return GenreService(repository)

@router.get("/", response_model=list[Genre])
def get_all_genres(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    service: GenreService = Depends(get_service),
):
    return service.get_all(skip=skip, limit=limit)

@router.get("/search", response_model=list[Genre])
def search_genres(
    name: str = Query(..., min_length=1),
    service: GenreService = Depends(get_service),
):
    return service.search_by_name(name)

@router.get("/{genre_id}", response_model=Genre)
def get_genre(genre_id: str, service: GenreService = Depends(get_service)):
    genre = service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre

@router.post("/", response_model=Genre, status_code=201)
def create_genre(data: GenreCreate, service: GenreService = Depends(get_service)):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{genre_id}", response_model=Genre)
def update_genre(
    genre_id: str,
    data: GenreUpdate,
    service: GenreService = Depends(get_service),
):
    genre = service.update(genre_id, data)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre

@router.delete("/{genre_id}", status_code=204)
def delete_genre(genre_id: str, service: GenreService = Depends(get_service)):
    deleted = service.delete(genre_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Genre not found")
