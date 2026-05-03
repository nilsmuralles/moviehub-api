from neo4j import Driver
from datetime import date

def _record_to_dict(record) -> dict:
    return dict(record["u"])

class AuthRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def find_by_username(self, username: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {username: $username})
                RETURN u
                """,
                username=username,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

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

    def create_user(self, user_id: str, username: str, password: str, is_premium: bool, avatar_path: str | None) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (u:User {
                    userId: $userId,
                    username: $username,
                    password: $password,
                    is_premium: $is_premium,
                    avatar_path: $avatar_path,
                    join_date: $join_date
                })
                RETURN u
                """,
                userId=user_id,
                username=username,
                password=password,
                is_premium=is_premium,
                avatar_path=avatar_path,
                join_date=date.today().strftime("%Y-%m-%d"),
            )
            return _record_to_dict(result.single())

    def create_interested_in(self, user_id: str, genre_ids: list[str]) -> None:
        today = date.today().strftime("%Y-%m-%d")
        with self.driver.session() as session:
            session.run(
                """
                UNWIND $genre_ids AS genreId
                MATCH (u:User {userId: $userId})
                MATCH (g:Genre {genreId: genreId})
                MERGE (u)-[r:INTERESTED_IN]->(g)
                SET r.affinity_score = 0.5,
                    r.total_watched = 0,
                    r.since = $since
                """,
                userId=user_id,
                genre_ids=genre_ids,
                since=today,
            )
