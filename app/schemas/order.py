from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemIn(BaseModel):
    sku: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(default=0, ge=0)


class OrderItemRead(OrderItemIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    status: OrderStatus = OrderStatus.PENDING
    order_date: date
    items: list[OrderItemIn] = Field(default_factory=list)


class OrderUpdate(BaseModel):
    customer_name: str | None = Field(default=None, min_length=1, max_length=255)
    status: OrderStatus | None = None
    order_date: date | None = None
    items: list[OrderItemIn] | None = None


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    status: str
    order_date: date
    items: list[OrderItemRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
