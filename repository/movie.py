from neo4j import Driver

from models.movie import MovieCreate, MovieUpdate

def _record_to_dict(record) -> dict:
    return dict(record["m"])

class MovieRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def find_all(self, skip: int, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)
                OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
                WITH m, collect(g.name) AS genres
                RETURN m, genres
                ORDER BY m.title
                SKIP $skip LIMIT $limit
                """,
                skip=skip,
                limit=limit,
            )
            records = []
            for r in result:
                movie = dict(r["m"])
                movie["genres"] = r["genres"] if r["genres"] else []
                records.append(movie)
            return records

    def find_by_id(self, movie_id: int) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie {movieId: $movieId})
                OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
                WITH m, collect(g.name) AS genres
                RETURN m, genres
                """,
                movieId=movie_id,
            )
            record = result.single()
            if not record:
                return None
            movie = dict(record["m"])
            movie["genres"] = record["genres"] if record["genres"] else []
            return movie

    def find_by_title(self, title: str) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)
                WHERE toLower(m.title) CONTAINS toLower($title)
                RETURN m
                ORDER BY m.title
                """,
                title=title,
            )
            return [_record_to_dict(r) for r in result]

    def create(self, data: MovieCreate) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (m:Movie {
                    movieId: $movieId,
                    title: $title,
                    release_date: $release_date,
                    overview: $overview,
                    vote_average: $vote_average,
                    vote_count: $vote_count,
                    poster_path: $poster_path,
                    backdrop_path: $backdrop_path,
                    genres: $genres,
                    is_adult: $is_adult,
                    budget: $budget,
                    homepage: $homepage,
                    revenue: $revenue,
                    runtime: $runtime,
                    status: $status
                })
                RETURN m
                """,
                **data.model_dump(),
            )
            return _record_to_dict(result.single())

    def update(self, movie_id: int, data: MovieUpdate) -> dict | None:
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if not fields:
            return self.find_by_id(movie_id)

        set_clause = ", ".join(f"m.{k} = ${k}" for k in fields)
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (m:Movie {{movieId: $movieId}})
                SET {set_clause}
                RETURN m
                """,
                movieId=movie_id,
                **fields,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def delete(self, movie_id: int) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie {movieId: $movieId})
                DETACH DELETE m
                RETURN count(m) AS deleted
                """,
                movieId=movie_id,
            )
            return result.single()["deleted"] > 0
        
    def find_by_genre(self, genre: str, skip: int, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
                WHERE toLower(g.name) = toLower($genre)
                RETURN m
                ORDER BY m.vote_average DESC
                SKIP $skip LIMIT $limit
                """,
                genre=genre,
                skip=skip,
                limit=limit,
            )
            return [_record_to_dict(r) for r in result]
        
    def add_genres(self, movie_id: int, genre_ids: list[str]) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (m:Movie {movieId: $movieId})
                UNWIND $genre_ids AS genreId
                MATCH (g:Genre {genreId: genreId})
                MERGE (m)-[:HAS_GENRE]->(g)
                """,
                movieId=movie_id,
                genre_ids=genre_ids,
            )
