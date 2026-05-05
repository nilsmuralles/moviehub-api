from neo4j import Driver
from models.genre import GenreCreate, GenreUpdate

def _record_to_dict(record) -> dict:
    return dict(record["g"])

class GenreRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def find_all(self, skip: int, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (g:Genre)
                RETURN g
                ORDER BY g.name
                SKIP $skip LIMIT $limit
                """,
                skip=skip,
                limit=limit,
            )
            return [_record_to_dict(r) for r in result]

    def find_by_id(self, genre_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (g:Genre {genreId: $genreId})
                RETURN g
                """,
                genreId=genre_id,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def find_by_name(self, name: str) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (g:Genre)
                WHERE toLower(g.name) CONTAINS toLower($name)
                RETURN g
                ORDER BY g.name
                """,
                name=name,
            )
            return [_record_to_dict(r) for r in result]

    def create(self, data: GenreCreate) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (g:Genre {
                    genreId: $genreId,
                    name: $name,
                    movie_count: $movie_count,
                    avg_rating: $avg_rating,
                    popularity_score: $popularity_score,
                    is_classic: $is_classic
                })
                RETURN g
                """,
                **data.model_dump(),
            )
            return _record_to_dict(result.single())

    def update(self, genre_id: str, data: GenreUpdate) -> dict | None:
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if not fields:
            return self.find_by_id(genre_id)

        set_clause = ", ".join(f"g.{k} = ${k}" for k in fields)
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (g:Genre {{genreId: $genreId}})
                SET {set_clause}
                RETURN g
                """,
                genreId=genre_id,
                **fields,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def delete(self, genre_id: str) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (g:Genre {genreId: $genreId})
                DETACH DELETE g
                RETURN count(g) AS deleted
                """,
                genreId=genre_id,
            )
            return result.single()["deleted"] > 0
        

    def update_genre_count(self, genre_id: str):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (g:Genre {genreId: $genreId})<-[:HAS_GENRE]-(m:Movie)
                WITH g, count(m) AS total
                SET g.movie_count = total
                """,
                genreId=genre_id
            )
