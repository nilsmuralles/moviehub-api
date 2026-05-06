from neo4j import Driver
from models.review import ReviewCreate, ReviewUpdate

def _record_to_dict(record) -> dict:
    return {
        **dict(record["r"]),
        "userId": record["userId"],
        "movieId": record["movieId"]
    }

class ReviewRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, data: ReviewCreate) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})
                MATCH (m:Movie {movieId: $movieId})
                CREATE (r:Review {
                    reviewId: $reviewId,
                    rating: $rating,
                    content: $content,
                    url: $url,
                    created_at: toString(datetime()),
                    updated_at: toString(datetime())
                })
                CREATE (u)-[:WROTE]->(r)
                CREATE (m)-[:HAS_REVIEW]->(r)
                RETURN r, u.userId AS userId, m.movieId AS movieId
                """,
                **data.model_dump(),
            )
            return _record_to_dict(result.single())

    def update(self, review_id: int, data: ReviewUpdate) -> dict | None:
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if not fields:
            return None

        set_clause = ", ".join(f"r.{k} = ${k}" for k in fields)

        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (r:Review {{reviewId: $reviewId}})
                SET {set_clause}
                RETURN r
                """,
                reviewId=review_id,
                **fields,
            )
            record = result.single()
            return dict(record["r"]) if record else None
    def find_all(self, skip: int, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (r:Review)
                OPTIONAL MATCH (u:User)-[:WROTE]->(r)
                OPTIONAL MATCH (r)-[:HAS_REVIEW]->(m:Movie)
                RETURN r, u.userId AS userId, m.movieId AS movieId
                ORDER BY r.created_at DESC
                SKIP $skip LIMIT $limit
                """,
                skip=skip, limit=limit,
            )
            return [_record_to_dict(r) for r in result]

    def find_by_id(self, review_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (r:Review {reviewId: $reviewId})
                OPTIONAL MATCH (u:User)-[:WROTE]->(r)
                OPTIONAL MATCH (r)-[:HAS_REVIEW]->(m:Movie)
                RETURN r, u.userId AS userId, m.movieId AS movieId
                """,
                reviewId=review_id,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def find_by_movie(self, movie_id: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (r:Review)-[:HAS_REVIEW]->(m:Movie {movieId: $movieId})
                OPTIONAL MATCH (u:User)-[:WROTE]->(r)
                RETURN r, u.userId AS userId, m.movieId AS movieId
                ORDER BY r.created_at DESC
                """,
                movieId=movie_id,
            )
            return [_record_to_dict(r) for r in result]

    def delete(self, review_id: str) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (r:Review {reviewId: $reviewId})
                DETACH DELETE r
                RETURN count(r) AS deleted
                """,
                reviewId=review_id,
            )
            return result.single()["deleted"] > 0
        
    def hide_reviews(self, review_ids: list[str]) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (r:Review)
                WHERE r.reviewId IN $reviewIds
                SET r.hidden = true
                """,
                reviewIds=review_ids,
            )

    def unhide_reviews(self, review_ids: list[str]) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (r:Review)
                WHERE r.reviewId IN $reviewIds
                REMOVE r.hidden
                """,
                reviewIds=review_ids,
            )

    def delete_reviews(self, review_ids: list[str]) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (r:Review)
                WHERE r.reviewId IN $reviewIds
                DETACH DELETE r
                """,
                reviewIds=review_ids,
            )

    def find_by_movie(self, movie_id: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (r:Review {movieId: $movieId})
                OPTIONAL MATCH (u:User)-[:WROTE]->(r)
                RETURN r, u.userId AS userId, r.movieId AS movieId
                ORDER BY r.created_at DESC
                """,
                movieId=movie_id,
            )
            return [_record_to_dict(rec) for rec in result]
