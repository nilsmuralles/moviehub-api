from repository.analytics import AnalyticsRepository

class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    def get_movie_financials(self) -> dict:
        return self.repository.get_movie_financials()

    def get_movie_financials_by_id(self, movie_id: int) -> dict | None:
        return self.repository.get_movie_financials_by_id(movie_id)

    def get_movies_by_status(self) -> list[dict]:
        return self.repository.get_movies_by_status()

    def get_movies_by_genre(self) -> list[dict]:
        return self.repository.get_movies_by_genre()

    def get_release_date_range(self) -> dict:
        return self.repository.get_release_date_range()

    def get_user_genres(self) -> list[dict]:
        return self.repository.get_user_genres()

    def get_movies_per_company(self) -> list[dict]:
        return self.repository.get_movies_per_company()

    def get_top_movies_by_rating(self) -> list[dict]:
        return self.repository.get_top_movies_by_rating()

    def get_movies_by_genre_name(self, genre: str) -> list[dict]:
        return self.repository.get_movies_by_genre_name(genre)
