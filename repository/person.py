from neo4j import Driver
from models.person import PersonCreate, PersonUpdate

def _record_to_dict(record) -> dict:
    return dict(record["p"])

def _labels_from_department(department: str | None) -> str:
    if department == "Acting":
        return "People:Actor"
    if department == "Directing":
        return "People:Director"
    return "People"

class PersonRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def find_all(self, skip: int, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:People)
                RETURN p
                ORDER BY p.name
                SKIP $skip LIMIT $limit
                """,
                skip=skip,
                limit=limit,
            )
            return [_record_to_dict(r) for r in result]

    def find_by_id(self, person_id: int) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:People {personId: $personId})
                RETURN p
                """,
                personId=person_id,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def find_by_name(self, name: str) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:People)
                WHERE toLower(p.name) CONTAINS toLower($name)
                RETURN p
                ORDER BY p.name
                """,
                name=name,
            )
            return [_record_to_dict(r) for r in result]

    def create(self, data: PersonCreate) -> dict:
        labels = _labels_from_department(data.known_for_department)
        with self.driver.session() as session:
            result = session.run(
                f"""
                CREATE (p:{labels} {{
                    personId: $personId,
                    name: $name,
                    known_for_department: $known_for_department,
                    popularity: $popularity,
                    gender: $gender,
                    profile_path: $profile_path
                }})
                RETURN p
                """,
                **data.model_dump(),
            )
            return _record_to_dict(result.single())

    def update(self, person_id: int, data: PersonUpdate) -> dict | None:
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if not fields:
            return self.find_by_id(person_id)

        set_clause = ", ".join(f"p.{k} = ${k}" for k in fields)

        extra_label = ""
        if "known_for_department" in fields:
            dept = fields["known_for_department"]
            if dept == "Acting":
                extra_label = "SET p:Actor"
            elif dept == "Directing":
                extra_label = "SET p:Director"

        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (p:People {{personId: $personId}})
                SET {set_clause}
                {extra_label}
                RETURN p
                """,
                personId=person_id,
                **fields,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def delete(self, person_id: int) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:People {personId: $personId})
                DETACH DELETE p
                RETURN count(p) AS deleted
                """,
                personId=person_id,
            )
            return result.single()["deleted"] > 0
