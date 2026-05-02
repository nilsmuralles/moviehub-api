from pydantic import BaseModel
from typing import Optional

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    headquarters: Optional[str] = None
    homepage: Optional[str] = None
    logo_path: Optional[str] = None
    origin_country: Optional[str] = None


class CompanyCreate(CompanyBase):
    companyId: int


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    headquarters: Optional[str] = None
    homepage: Optional[str] = None
    logo_path: Optional[str] = None
    origin_country: Optional[str] = None


class Company(CompanyBase):
    companyId: int

    class Config:
        from_attributes = True