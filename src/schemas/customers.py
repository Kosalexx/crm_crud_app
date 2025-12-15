from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime


class CustomerAddSchema(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    email: EmailStr | None = None
    phones: list[str] | None = None
    birthday: datetime | None = None

    model_config = {"populate_by_name": True}


class CustomerGetSchema(CustomerAddSchema):
    id: int

    @field_validator("phones", mode="before")
    @classmethod
    def parse_phones(cls, v):
        """
        Validator for converting phones from list of dicts to list of strings.
        """
        if v is None:
            return None
        if isinstance(v, list):
            if not v:
                return []
            if isinstance(v[0], dict):
                return [item.get("number") for item in v if item.get("number")]
            if isinstance(v[0], str):
                return v
        return v


class CustomerResponseWithIdOnlySchema(BaseModel):
    id: int


class CustomerFiltersSchema(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    created_at_from: str | None = None
    created_at_to: str | None = None
    limit: int = 20
    page: int = 1


class CustomersListResponseSchema(BaseModel):
    """Модель ответа для списка клиентов"""

    customers: list[CustomerGetSchema]
    pagination: dict | None = None


class CustomerGetOrdersSchema(BaseModel):
    customer_id: int = Field(alias="customerId")
    limit: int = 20
    page: int = 1

    model_config = {"populate_by_name": True}
