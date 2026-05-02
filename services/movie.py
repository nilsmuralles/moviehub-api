from models.movie import Movie, MovieCreate, MovieUpdate
from repository.movie import MovieRepository

class MovieService:
    def __init__(self, repository: MovieRepository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 25) -> list[Movie]:
        records = self.repository.find_all(skip=skip, limit=limit)
        return [Movie(**r) for r in records]

    def get_by_id(self, movie_id: int) -> Movie | None:
        record = self.repository.find_by_id(movie_id)
        return Movie(**record) if record else None

    def search_by_title(self, title: str) -> list[Movie]:
        records = self.repository.find_by_title(title)
        return [Movie(**r) for r in records]

    def create(self, data: MovieCreate) -> Movie:
        existing = self.repository.find_by_id(data.movieId)
        if existing:
            raise ValueError(f"Movie with id {data.movieId} already exists")
        record = self.repository.create(data)
        return Movie(**record)

    def update(self, movie_id: int, data: MovieUpdate) -> Movie | None:
        record = self.repository.update(movie_id, data)
        return Movie(**record) if record else None

    def delete(self, movie_id: int) -> bool:
        return self.repository.delete(movie_id)
