from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_driver
from models.user import User, UserCreate, UserUpdate
from repository.user import UserRepository
from services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_service() -> UserService:
    driver = get_driver()
    repository = UserRepository(driver)
    return UserService(repository)


@router.get("/", response_model=list[User])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    service: UserService = Depends(get_service),
):
    return service.get_all(skip=skip, limit=limit)


@router.get("/search", response_model=list[User])
def search_users(
    username: str = Query(..., min_length=1),
    service: UserService = Depends(get_service),
):
    return service.search_by_username(username)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str, service: UserService = Depends(get_service)):
    user = service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User, status_code=201)
def create_user(data: UserCreate, service: UserService = Depends(get_service)):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/{user_id}", response_model=User)
def update_user(
    user_id: str,
    data: UserUpdate,
    service: UserService = Depends(get_service),
):
    user = service.update(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, service: UserService = Depends(get_service)):
    deleted = service.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/{user_id}/watched/{movie_id}/toggle")
def toggle_watched(user_id: str, movie_id: int, service: UserService = Depends(get_service)):
    return service.toggle_watched(user_id, movie_id)

@router.get("/{user_id}/watched/{movie_id}")
def is_watching(user_id: str, movie_id: int, service: UserService = Depends(get_service)):
    result = service.is_watching(user_id, movie_id)
    return result

@router.patch("/{user_id}/watched/{movie_id}/progress")
def update_watch_progress(
    user_id: str,
    movie_id: int,
    progress: float = Query(..., ge=0.0, le=100.0, description="Percentage watched so far"),
    service: UserService = Depends(get_service),
):
    updated = service.update_watch_progress(user_id, movie_id, progress)
    if not updated:
        raise HTTPException(status_code=404, detail="WATCHED relationship not found")
    return {"userId": user_id, "movieId": movie_id, "progress_percentage": progress}

@router.get("/{user_id}/watched")
def get_watched_movies(user_id: str, service: UserService = Depends(get_service)):
    return service.get_watched_movies(user_id)

@router.get("/{user_id}/recommended")
def get_recommended_movies(user_id: str, service: UserService = Depends(get_service)):
    return service.get_recommended_movies(user_id)

@router.get("/{user_id}/reviews")
def get_user_reviews(user_id: str, service: UserService = Depends(get_service)):
    return service.get_user_reviews(user_id)

@router.delete("/{user_id}/watched", status_code=200)
def clear_watch_history(user_id: str, service: UserService = Depends(get_service)):
    deleted = service.clear_watch_history(user_id)
    return {"userId": user_id, "relationships_deleted": deleted}
