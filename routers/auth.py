from fastapi import APIRouter, Depends, HTTPException
from database import get_driver
from models.auth import SignUpRequest, GenreSelectionRequest, LoginRequest, LoginResponse
from models.user import User
from repository.auth import AuthRepository
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

def get_service() -> AuthService:
    driver = get_driver()
    repository = AuthRepository(driver)
    return AuthService(repository)

@router.post("/signup", response_model=User, status_code=201)
def sign_up(data: SignUpRequest, service: AuthService = Depends(get_service)):
    try:
        return service.sign_up(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/signup/genres", status_code=204)
def select_genres(data: GenreSelectionRequest, service: AuthService = Depends(get_service)):
    try:
        service.select_genres(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, service: AuthService = Depends(get_service)):
    try:
        return service.login(data)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
