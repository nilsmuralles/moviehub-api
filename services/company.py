from models.company import Company, CompanyCreate, CompanyUpdate
from repository.company import CompanyRepository

class CompanyService:
    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 25) -> list[Company]:
        records = self.repository.find_all(skip=skip, limit=limit)
        return [Company(**r) for r in records]

    def get_by_id(self, company_id: int) -> Company | None:
        record = self.repository.find_by_id(company_id)
        return Company(**record) if record else None

    def create(self, data: CompanyCreate) -> Company:
        existing = self.repository.find_by_id(data.companyId)
        if existing:
            raise ValueError(f"Company with id {data.companyId} already exists")

        record = self.repository.create(data)
        return Company(**record)

    def update(self, company_id: int, data: CompanyUpdate) -> Company | None:
        record = self.repository.update(company_id, data)
        return Company(**record) if record else None

    def delete(self, company_id: int) -> bool:
        return self.repository.delete(company_id)