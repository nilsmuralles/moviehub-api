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
                    created_at: $created_at
                })

                CREATE (u)-[:WROTE]->(r)
                CREATE (r)-[:REVIEWS]->(m)

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