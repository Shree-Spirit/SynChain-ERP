from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InvoiceStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    OVERDUE = "overdue"


class InvoiceCreate(BaseModel):
    order_id: int | None = Field(default=None, ge=1)
    purchase_order_id: int | None = Field(default=None, ge=1)
    amount: Decimal = Field(..., gt=0)
    status: InvoiceStatus = InvoiceStatus.UNPAID
    due_date: date | None = None

    @model_validator(mode="after")
    def exactly_one_source(self) -> "InvoiceCreate":
        if bool(self.order_id) == bool(self.purchase_order_id):
            raise ValueError("Provide exactly one of order_id or purchase_order_id")
        return self


class InvoiceUpdate(BaseModel):
    order_id: int | None = Field(default=None, ge=1)
    purchase_order_id: int | None = Field(default=None, ge=1)
    amount: Decimal | None = Field(default=None, gt=0)
    status: InvoiceStatus | None = None
    due_date: date | None = None


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int | None
    purchase_order_id: int | None
    amount: Decimal
    status: str
    due_date: date | None
    created_at: datetime
    updated_at: datetime
