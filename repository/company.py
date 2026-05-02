from neo4j import Driver
from models.company import CompanyCreate, CompanyUpdate

def _record_to_dict(record) -> dict:
    return dict(record["c"])


class CompanyRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def find_all(self, skip: int, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Company)
                RETURN c
                ORDER BY c.name
                SKIP $skip LIMIT $limit
                """,
                skip=skip,
                limit=limit,
            )
            return [_record_to_dict(r) for r in result]

    def find_by_id(self, company_id: int) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Company {companyId: $companyId})
                RETURN c
                """,
                companyId=company_id,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def create(self, data: CompanyCreate) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (c:Company {
                    companyId: $companyId,
                    name: $name,
                    description: $description,
                    headquarters: $headquarters,
                    homepage: $homepage,
                    logo_path: $logo_path,
                    origin_country: $origin_country
                })
                RETURN c
                """,
                **data.model_dump(),
            )
            return _record_to_dict(result.single())

    def update(self, company_id: int, data: CompanyUpdate) -> dict | None:
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if not fields:
            return self.find_by_id(company_id)

        set_clause = ", ".join(f"c.{k} = ${k}" for k in fields)

        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (c:Company {{companyId: $companyId}})
                SET {set_clause}
                RETURN c
                """,
                companyId=company_id,
                **fields,
            )
            record = result.single()
            return _record_to_dict(record) if record else None

    def delete(self, company_id: int) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Company {companyId: $companyId})
                DETACH DELETE c
                RETURN count(c) AS deleted
                """,
                companyId=company_id,
            )
            return result.single()["deleted"] > 0