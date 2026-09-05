from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.warehouse import Warehouse
from app.repositories.warehouse_repository import WarehouseRepository
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from app.utils.pagination import PaginationParams


class WarehouseService:
    def __init__(self, db: Session) -> None:
        self.repo = WarehouseRepository(db)

    def get(self, warehouse_id: int) -> Warehouse:
        warehouse = self.repo.get_by_id(warehouse_id)
        if warehouse is None:
            raise NotFoundError(f"Warehouse {warehouse_id} not found")
        return warehouse

    def list(
        self,
        pagination: PaginationParams,
        location: str | None = None,
        name: str | None = None,
    ) -> tuple[list[Warehouse], int]:
        return self.repo.list_paginated(
            pagination, self.repo.filtered_query(location=location, name=name)
        )

    def create(self, payload: WarehouseCreate) -> Warehouse:
        return self.repo.add(Warehouse(**payload.model_dump()))

    def update(self, warehouse_id: int, payload: WarehouseUpdate) -> Warehouse:
        warehouse = self.get(warehouse_id)
        return self.repo.apply_updates(warehouse, payload.model_dump(exclude_unset=True))

    def delete(self, warehouse_id: int) -> None:
        warehouse = self.get(warehouse_id)
        try:
            self.repo.delete(warehouse)
        except IntegrityError as exc:
            raise ConflictError("Cannot delete warehouse that still has inventory items") from exc
