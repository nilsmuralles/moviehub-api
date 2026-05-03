from models.genre import Genre, GenreCreate, GenreUpdate
from repository.genre import GenreRepository

class GenreService:
    def __init__(self, repository: GenreRepository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 25) -> list[Genre]:
        records = self.repository.find_all(skip=skip, limit=limit)
        return [Genre(**r) for r in records]

    def get_by_id(self, genre_id: str) -> Genre | None:
        record = self.repository.find_by_id(genre_id)
        return Genre(**record) if record else None

    def search_by_name(self, name: str) -> list[Genre]:
        records = self.repository.find_by_name(name)
        return [Genre(**r) for r in records]

    def create(self, data: GenreCreate) -> Genre:
        existing = self.repository.find_by_id(data.genreId)
        if existing:
            raise ValueError(f"Genre with id {data.genreId} already exists")
        record = self.repository.create(data)
        return Genre(**record)

    def update(self, genre_id: str, data: GenreUpdate) -> Genre | None:
        record = self.repository.update(genre_id, data)
        return Genre(**record) if record else None

    def delete(self, genre_id: str) -> bool:
        return self.repository.delete(genre_id)
