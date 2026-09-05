from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.supplier import Supplier
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.utils.pagination import PaginationParams


class SupplierService:
    def __init__(self, db: Session) -> None:
        self.repo = SupplierRepository(db)

    def get(self, supplier_id: int) -> Supplier:
        supplier = self.repo.get_by_id(supplier_id)
        if supplier is None:
            raise NotFoundError(f"Supplier {supplier_id} not found")
        return supplier

    def list(
        self,
        pagination: PaginationParams,
        name: str | None = None,
        category: str | None = None,
    ) -> tuple[list[Supplier], int]:
        return self.repo.list_paginated(pagination, self.repo.filtered_query(name, category))

    def create(self, payload: SupplierCreate) -> Supplier:
        return self.repo.add(Supplier(**payload.model_dump()))

    def update(self, supplier_id: int, payload: SupplierUpdate) -> Supplier:
        supplier = self.get(supplier_id)
        data = payload.model_dump(exclude_unset=True)
        return self.repo.apply_updates(supplier, data)

    def delete(self, supplier_id: int) -> None:
        supplier = self.get(supplier_id)
        try:
            self.repo.delete(supplier)
        except IntegrityError as exc:
            raise ConflictError("Cannot delete supplier that has related purchase orders") from exc
