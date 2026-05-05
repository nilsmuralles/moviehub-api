from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_driver
from models.user import User, UserCreate, UserUpdate, GenreUpdate
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
def get_user(user_id: int, service: UserService = Depends(get_service)):
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
    user_id: int,
    data: UserUpdate,
    service: UserService = Depends(get_service),
):
    user = service.update(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, service: UserService = Depends(get_service)):
    deleted = service.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    
# Películas vistas
@router.post("/{user_id}/watched/{movie_id}/toggle")
@router.post("/{user_id}/watched/{movie_id}/toggle/")
def toggle_watched(user_id: str, movie_id: int, service: UserService = Depends(get_service)):
    return service.toggle_watched(user_id, movie_id)

# Recomendaciones
@router.post("/{user_id}/recommend/{movie_id}")
def add_recommend(
    user_id: int,
    movie_id: int,
    service: UserService = Depends(get_service),
):
    service.add_recommend(user_id, movie_id)
    return {"message": "Movie recommended"}

@router.delete("/{user_id}/recommend/{movie_id}")
def remove_recommend(
    user_id: int,
    movie_id: int,
    service: UserService = Depends(get_service),
):
    service.remove_recommend(user_id, movie_id)
    return {"message": "Recommendation removed"}

# Usuarios seguidos
@router.post("/{user_id}/follow/{target_id}")
def follow_user(
    user_id: int,
    target_id: int,
    service: UserService = Depends(get_service),
):
    try:
        service.follow_user(user_id, target_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Now following user"}

@router.delete("/{user_id}/follow/{target_id}")
def unfollow_user(
    user_id: int,
    target_id: int,
    service: UserService = Depends(get_service),
):
    service.unfollow_user(user_id, target_id)
    return {"message": "Unfollowed user"}

# Géneros
@router.put("/{user_id}/genres")
def update_genres(
    user_id: int,
    data: GenreUpdate,
    service: UserService = Depends(get_service),
):
    service.set_genres(user_id, data.genres)
    return {"message": "Genres updated"}

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

@router.patch("/{user_id}/toggle-premium", response_model=User)
def toggle_premium(user_id: str, service: UserService = Depends(get_service)):
    user = service.toggle_premium(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}/verify-reviews", status_code=200)
def verify_premium_reviews(user_id: str, service: UserService = Depends(get_service)):
    updated = service.verify_premium_reviews(user_id)
    if updated == 0:
        raise HTTPException(status_code=400, detail="User not found or not premium")
    return {"userId": user_id, "reviews_verified": updated}

@router.patch("/{user_id}/verify")
def toggle_verified(user_id: int, service: UserService = Depends(get_service)):
    user = service.toggle_verified(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
