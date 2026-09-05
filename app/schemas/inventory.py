from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryItemBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(..., ge=0)
    unit: str = Field(default="pcs", min_length=1, max_length=30)
    reorder_level: int = Field(default=0, ge=0)
    warehouse_id: int = Field(..., ge=1)


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=80)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: int | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    reorder_level: int | None = Field(default=None, ge=0)
    warehouse_id: int | None = Field(default=None, ge=1)


class InventoryItemRead(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
