from neo4j import Driver
from models.user import UserCreate, UserUpdate
import json

def _record_to_dict(record) -> dict:
    data = dict(record["u"])
    if isinstance(data.get("genres"), str):
        try:
            data["genres"] = json.loads(data["genres"])
        except (ValueError, TypeError):
            data["genres"] = []
    return data

class UserRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def find_all(self, skip: int, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)
                RETURN u
                ORDER BY u.username
                SKIP $skip LIMIT $limit
                """,
                skip=skip,
                limit=limit,
            )
            return [_record_to_dict(r) for r in result]

    def find_by_id(self, user_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})
                RETURN u
                """,
                userId=user_id,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def find_by_username(self, username: str) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)
                WHERE toLower(u.username) CONTAINS toLower($username)
                RETURN u
                ORDER BY u.username
                """,
                username=username,
            )
            return [_record_to_dict(r) for r in result]

    def create(self, data: UserCreate) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (u:User {
                    userId: $userId,
                    username: $username,
                    password: $password,
                    is_premium: $is_premium,
                    avatar_path: $avatar_path,
                    join_date: date()
                })
                RETURN u
                """,
                **data.model_dump(),
            )
            return _record_to_dict(result.single())

    def update(self, user_id: str, data: UserUpdate) -> dict | None:
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if not fields:
            return self.find_by_id(user_id)

        set_clause = ", ".join(f"u.{k} = ${k}" for k in fields)
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (u:User {{userId: $userId}})
                SET {set_clause}
                RETURN u
                """,
                userId=user_id,
                **fields,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def delete(self, user_id: str) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})
                DETACH DELETE u
                RETURN count(u) AS deleted
                """,
                userId=user_id,
            )
            return result.single()["deleted"] > 0
        
    # Películas vistas
    def add_watched(self, user_id: int, movie_id: int):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {userId: $userId})
                MATCH (m:Movie {movieId: $movieId})
                MERGE (u)-[:WATCHED]->(m)
                """,
                userId=user_id,
                movieId=movie_id
            )

    def remove_watched(self, user_id: int, movie_id: int):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {userId: $userId})-[r:WATCHED]->(m:Movie {movieId: $movieId})
                DELETE r
                """,
                userId=user_id,
                movieId=movie_id
            )

    # Recomendaciones
    def add_recommend(self, user_id: int, movie_id: int):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {userId: $userId})
                MATCH (m:Movie {movieId: $movieId})
                MERGE (u)-[:RECOMMENDS]->(m)
                """,
                userId=user_id,
                movieId=movie_id
            )

    def remove_recommend(self, user_id: int, movie_id: int):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {userId: $userId})-[r:RECOMMENDS]->(m:Movie {movieId: $movieId})
                DELETE r
                """,
                userId=user_id,
                movieId=movie_id
            )

    # Seguir usuarios

    def follow_user(self, user_id: int, target_id: int):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {userId: $userId})
                MATCH (t:User {userId: $targetId})
                MERGE (u)-[:FOLLOWS]->(t)
                """,
                userId=user_id,
                targetId=target_id
            )

    def unfollow_user(self, user_id: int, target_id: int):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {userId: $userId})-[r:FOLLOWS]->(t:User {userId: $targetId})
                DELETE r
                """,
                userId=user_id,
                targetId=target_id
            )

    # Géneros de interés
    def set_user_genres(self, user_id: int, genres: list[str]):
        with self.driver.session() as session:
            # eliminar relaciones existentes
            session.run(
                """
                MATCH (u:User {userId: $userId})-[r:INTERESTED_IN]->(:Genre)
                DELETE r
                """,
                userId=user_id
            )

            # crear nuevas
            for genre in genres:
                session.run(
                    """
                    MATCH (u:User {userId: $userId})
                    MERGE (g:Genre {name: $genre})
                    MERGE (u)-[:INTERESTED_IN]->(g)
                    """,
                    userId=user_id,
                    genre=genre
                )

    def update_watch_progress(self, user_id: str, movie_id: int, progress: float) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})-[r:WATCHED]->(m:Movie {movieId: $movieId})
                SET r.progress_percentage = $progress
                RETURN count(r) AS updated
                """,
                userId=user_id,
                movieId=movie_id,
                progress=progress,
            )
            return result.single()["updated"] > 0

    def toggle_premium(self, user_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})
                SET u.is_premium = NOT coalesce(u.is_premium, false)
                RETURN u
                """,
                userId=user_id,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def verify_premium_reviews(self, user_id: str) -> int:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId, is_premium: true})-[r:WROTE]->(:Review)
                SET r.is_verified = true
                RETURN count(r) AS updated
                """,
                userId=user_id,
            )
            return result.single()["updated"]
        
    def toggle_verified(self, user_id: int) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})
                WITH u,
                    CASE 
                        WHEN exists(u.verified) THEN false
                        ELSE true
                    END AS shouldVerify
                FOREACH (_ IN CASE WHEN shouldVerify THEN [1] ELSE [] END |
                    SET u.verified = true
                )
                FOREACH (_ IN CASE WHEN NOT shouldVerify THEN [1] ELSE [] END |
                    REMOVE u.verified
                )
                RETURN u
                """,
                userId=user_id
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def toggle_watched(self, user_id: str, movie_id: int) -> dict:
        with self.driver.session() as session:
            existing = session.run(
                """
                MATCH (u:User {userId: $userId})-[w:WATCHED]->(m:Movie {movieId: $movieId})
                RETURN w
                """,
                userId=user_id,
                movieId=movie_id,
            ).single()

            if existing:
                session.run(
                    """
                    MATCH (u:User {userId: $userId})-[w:WATCHED]->(m:Movie {movieId: $movieId})
                    DELETE w
                    """,
                    userId=user_id,
                    movieId=movie_id,
                )
                return {"status": "removed"}
            else:
                session.run(
                    """
                    MATCH (u:User {userId: $userId}), (m:Movie {movieId: $movieId})
                    CREATE (u)-[:WATCHED {progress_percentage: 100}]->(m)
                    """,
                    userId=user_id,
                    movieId=movie_id,
                )
                return {"status": "added"}
