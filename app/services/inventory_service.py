from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.inventory import InventoryItem
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate
from app.utils.pagination import PaginationParams


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.repo = InventoryRepository(db)
        self.warehouses = WarehouseRepository(db)

    def _ensure_warehouse(self, warehouse_id: int) -> None:
        if self.warehouses.get_by_id(warehouse_id) is None:
            raise BadRequestError(f"Warehouse {warehouse_id} does not exist")

    def get(self, item_id: int) -> InventoryItem:
        item = self.repo.get_by_id(item_id)
        if item is None:
            raise NotFoundError(f"Inventory item {item_id} not found")
        return item

    def list(
        self,
        pagination: PaginationParams,
        warehouse_id: int | None = None,
        sku: str | None = None,
        name: str | None = None,
    ) -> tuple[list[InventoryItem], int]:
        return self.repo.list_paginated(
            pagination,
            self.repo.filtered_query(warehouse_id=warehouse_id, sku=sku, name=name),
        )

    def create(self, payload: InventoryItemCreate) -> InventoryItem:
        self._ensure_warehouse(payload.warehouse_id)
        if self.repo.get_by_sku(payload.sku):
            raise ConflictError(f"SKU '{payload.sku}' already exists")
        try:
            return self.repo.add(InventoryItem(**payload.model_dump()))
        except IntegrityError as exc:
            raise ConflictError("Inventory item could not be created (duplicate SKU)") from exc

    def update(self, item_id: int, payload: InventoryItemUpdate) -> InventoryItem:
        item = self.get(item_id)
        data = payload.model_dump(exclude_unset=True)
        if "warehouse_id" in data:
            self._ensure_warehouse(data["warehouse_id"])
        if "sku" in data and data["sku"] != item.sku and self.repo.get_by_sku(data["sku"]):
            raise ConflictError(f"SKU '{data['sku']}' already exists")
        try:
            return self.repo.apply_updates(item, data)
        except IntegrityError as exc:
            raise ConflictError("Inventory item could not be updated") from exc

    def delete(self, item_id: int) -> None:
        self.repo.delete(self.get(item_id))
