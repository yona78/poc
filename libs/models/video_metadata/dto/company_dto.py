from pydantic import BaseModel

from ..types.company import Company


class CompanyDTO(BaseModel):
    id: int
    name: str

    class Config:
        extra = "forbid"

    def to_domain(self) -> Company:
        return Company(id=self.id, name=self.name)

    @classmethod
    def from_domain(cls, company: Company) -> "CompanyDTO":
        return cls(id=company.id, name=company.name)
