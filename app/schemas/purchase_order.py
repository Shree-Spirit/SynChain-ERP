from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PurchaseOrderStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class PurchaseOrderItemIn(BaseModel):
    sku: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(default=0, ge=0)


class PurchaseOrderItemRead(PurchaseOrderItemIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    purchase_order_id: int


class PurchaseOrderCreate(BaseModel):
    supplier_id: int = Field(..., ge=1)
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    expected_date: date | None = None
    items: list[PurchaseOrderItemIn] = Field(default_factory=list)


class PurchaseOrderUpdate(BaseModel):
    supplier_id: int | None = Field(default=None, ge=1)
    status: PurchaseOrderStatus | None = None
    expected_date: date | None = None
    items: list[PurchaseOrderItemIn] | None = None


class PurchaseOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier_id: int
    status: str
    expected_date: date | None
    items: list[PurchaseOrderItemRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
