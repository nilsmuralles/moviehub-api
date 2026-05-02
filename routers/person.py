from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_driver
from models.person import Person, PersonCreate, PersonUpdate
from repository.person import PersonRepository
from services.person import PersonService

router = APIRouter(prefix="/people", tags=["people"])

def get_service() -> PersonService:
    driver = get_driver()
    repository = PersonRepository(driver)
    return PersonService(repository)

@router.get("/", response_model=list[Person])
def get_all_people(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    service: PersonService = Depends(get_service),
):
    return service.get_all(skip=skip, limit=limit)

@router.get("/search", response_model=list[Person])
def search_people(
    name: str = Query(..., min_length=1),
    service: PersonService = Depends(get_service),
):
    return service.search_by_name(name)

@router.get("/{person_id}", response_model=Person)
def get_person(person_id: int, service: PersonService = Depends(get_service)):
    person = service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@router.post("/", response_model=Person, status_code=201)
def create_person(data: PersonCreate, service: PersonService = Depends(get_service)):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{person_id}", response_model=Person)
def update_person(
    person_id: int,
    data: PersonUpdate,
    service: PersonService = Depends(get_service),
):
    person = service.update(person_id, data)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: int, service: PersonService = Depends(get_service)):
    deleted = service.delete(person_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")
