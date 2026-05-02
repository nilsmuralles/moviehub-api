from neo4j import Driver
from models.user import UserCreate, UserUpdate

def _record_to_dict(record) -> dict:
    return dict(record["u"])

class UserRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def find_all(self, skip: int, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)
                RETURN u
                ORDER BY u.name
                SKIP $skip LIMIT $limit
                """,
                skip=skip,
                limit=limit,
            )
            return [_record_to_dict(r) for r in result]

    def find_by_id(self, user_id: int) -> dict | None:
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

    def find_by_name(self, name: str) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)
                WHERE toLower(u.name) CONTAINS toLower($name)
                RETURN u
                ORDER BY u.name
                """,
                name=name,
            )
            return [_record_to_dict(r) for r in result]

    def create(self, data: UserCreate) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (u:User {
                    userId: $userId,
                    name: $name,
                    password: $password,
                    is_premium: $is_premium,
                    join_date:$join_date,
                    genres: $genres,
                    avatar_path: $avatar_path
                })
                RETURN u
                """,
                **data.model_dump(),
            )
            return _record_to_dict(result.single())

    def update(self, user_id: int, data: UserUpdate) -> dict | None:
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if not fields:
            return self.find_by_id(user_id)

        set_clause = ", ".join(f"p.{k} = ${k}" for k in fields)

        extra_label = ""
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

    def delete(self, user_id: int) -> bool:
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
