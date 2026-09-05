from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = None
    category: str | None = Field(default=None, max_length=100)
    performance_rating: Decimal | None = Field(default=None, ge=0, le=5)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    contact_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    address: str | None = None
    category: str | None = Field(default=None, max_length=100)
    performance_rating: Decimal | None = Field(default=None, ge=0, le=5)


class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
