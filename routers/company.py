from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_driver
from models.company import Company, CompanyCreate, CompanyUpdate
from repository.company import CompanyRepository
from services.company import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])

def get_service() -> CompanyService:
    driver = get_driver()
    repository = CompanyRepository(driver)
    return CompanyService(repository)

@router.get("/", response_model=list[Company])
def get_all_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    service: CompanyService = Depends(get_service),
):
    return service.get_all(skip=skip, limit=limit)


@router.get("/{company_id}", response_model=Company)
def get_company(company_id: int, service: CompanyService = Depends(get_service)):
    company = service.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=Company, status_code=201)
def create_company(data: CompanyCreate, service: CompanyService = Depends(get_service)):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/{company_id}", response_model=Company)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    service: CompanyService = Depends(get_service),
):
    company = service.update(company_id, data)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: int, service: CompanyService = Depends(get_service)):
    deleted = service.delete(company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")