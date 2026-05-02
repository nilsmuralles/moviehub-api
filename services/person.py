from models.person import Person, PersonCreate, PersonUpdate
from repository.person import PersonRepository

class PersonService:
    def __init__(self, repository: PersonRepository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 25) -> list[Person]:
        records = self.repository.find_all(skip=skip, limit=limit)
        return [Person(**r) for r in records]

    def get_by_id(self, person_id: int) -> Person | None:
        record = self.repository.find_by_id(person_id)
        return Person(**record) if record else None

    def search_by_name(self, name: str) -> list[Person]:
        records = self.repository.find_by_name(name)
        return [Person(**r) for r in records]

    def create(self, data: PersonCreate) -> Person:
        existing = self.repository.find_by_id(data.personId)
        if existing:
            raise ValueError(f"Person with id {data.personId} already exists")
        record = self.repository.create(data)
        return Person(**record)

    def update(self, person_id: int, data: PersonUpdate) -> Person | None:
        record = self.repository.update(person_id, data)
        return Person(**record) if record else None

    def delete(self, person_id: int) -> bool:
        return self.repository.delete(person_id)
