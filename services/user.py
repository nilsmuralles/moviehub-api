from models.user import User, UserCreate, UserUpdate
from repository.user import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 25) -> list[User]:
        records = self.repository.find_all(skip=skip, limit=limit)
        return [User(**r) for r in records]

    def get_by_id(self, user_id: str) -> User | None:
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

    def update(self, user_id: str, data: UserUpdate) -> User | None:
        record = self.repository.update(user_id, data)
        return User(**record) if record else None

    def delete(self, user_id: str) -> bool:
        return self.repository.delete(user_id)
