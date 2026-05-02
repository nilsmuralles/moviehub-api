from models.user import User, UserCreate, UserUpdate
from repository.user import UserRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 25) -> list[User]:
        records = self.repository.find_all(skip=skip, limit=limit)
        return [User(**r) for r in records]

    def get_by_id(self, user_id: int) -> User | None:
        record = self.repository.find_by_id(user_id)
        return User(**record) if record else None

    def search_by_name(self, name: str) -> list[User]:
        records = self.repository.find_by_name(name)
        return [User(**r) for r in records]

    def create(self, data: UserCreate) -> User:
        existing = self.repository.find_by_id(data.userId)
        if existing:
            raise ValueError(f"User with id {data.userId} already exists")
        
        data.password = hash_password(data.password)

        record = self.repository.create(data)
        return User(**record)

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        if data.password is not None and pwd_context.identify(data.password) is None:
            data.password = hash_password(data.password)
        record = self.repository.update(user_id, data)
        return User(**record) if record else None

    def delete(self, user_id: int) -> bool:
        return self.repository.delete(user_id)