import uuid
from models.auth import SignUpRequest, GenreSelectionRequest, LoginRequest, LoginResponse
from models.user import User
from repository.auth import AuthRepository

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def sign_up(self, data: SignUpRequest) -> User:
        existing = self.repository.find_by_username(data.username)
        if existing:
            raise ValueError(f"Username '{data.username}' is already taken")

        user_id = f"u_{uuid.uuid4().hex[:8]}"
        record = self.repository.create_user(
            user_id=user_id,
            username=data.username,
            password=data.password,
            is_premium=data.is_premium or False,
            avatar_path=data.avatar_path,
        )
        return User(**record)

    def select_genres(self, data: GenreSelectionRequest) -> None:
        if len(data.genre_ids) != 3:
            raise ValueError("Exactly 3 genres must be selected")

        user = self.repository.find_by_id(data.userId)
        if not user:
            raise ValueError(f"User {data.userId} not found")

        self.repository.create_interested_in(data.userId, data.genre_ids)

    def login(self, data: LoginRequest) -> LoginResponse:
        record = self.repository.find_by_username(data.username)
        if not record:
            raise ValueError("Invalid username or password")
        if record["password"] != data.password:
            raise ValueError("Invalid username or password")

        return LoginResponse(
            userId=record["userId"],
            username=record["username"],
            is_premium=record.get("is_premium", False),
            join_date=record.get("join_date"),
            avatar_path=record.get("avatar_path"),
        )
