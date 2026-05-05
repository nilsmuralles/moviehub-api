from models.user import User, UserCreate, UserUpdate
from repository.user import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 25) -> list[User]:
        records = self.repository.find_all(skip=skip, limit=limit)
        return [User(**r) for r in records]

    def get_by_id(self, user_id: int) -> User | None:
        record = self.repository.find_by_id(user_id)
        return User(**record) if record else None

    def search_by_username(self, username: str) -> list[User]:
        records = self.repository.find_by_username(username)
        return [User(**r) for r in records]

    def create(self, data: UserCreate) -> User:
        existing = self.repository.find_by_id(data.userId)
        if existing:
            raise ValueError(f"User with id {data.userId} already exists")
        record = self.repository.create(data)
        return User(**record)

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        record = self.repository.update(user_id, data)
        return User(**record) if record else None

    def delete(self, user_id: int) -> bool:
        return self.repository.delete(user_id)
    
# ----- RELACIONES -----

    # Películas vistas
    def add_watched(self, user_id: int, movie_id: int):
        self.repository.add_watched(user_id, movie_id)

    def remove_watched(self, user_id: int, movie_id: int):
        self.repository.remove_watched(user_id, movie_id)

    # Recomendaciones
    def add_recommend(self, user_id: int, movie_id: int):
        self.repository.add_recommend(user_id, movie_id)

    def remove_recommend(self, user_id: int, movie_id: int):
        self.repository.remove_recommend(user_id, movie_id)

    # Seguir usuarios 
    def follow_user(self, user_id: int, target_id: int):
        if user_id == target_id:
            raise ValueError("User cannot follow themselves")
        self.repository.follow_user(user_id, target_id)

    def unfollow_user(self, user_id: int, target_id: int):
        self.repository.unfollow_user(user_id, target_id)

    # Géneros de interés
    def set_genres(self, user_id: int, genres: list[str]):
        self.repository.set_user_genres(user_id, genres)

    def update_watch_progress(self, user_id: str, movie_id: int, progress: float) -> bool:
        return self.repository.update_watch_progress(user_id, movie_id, progress)

    def toggle_premium(self, user_id: str) -> User | None:
        record = self.repository.toggle_premium(user_id)
        return User(**record) if record else None

    def verify_premium_reviews(self, user_id: str) -> int:
        return self.repository.verify_premium_reviews(user_id)
