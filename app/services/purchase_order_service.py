from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderItemIn, PurchaseOrderUpdate
from app.utils.pagination import PaginationParams


class PurchaseOrderService:
    def __init__(self, db: Session) -> None:
        self.repo = PurchaseOrderRepository(db)
        self.suppliers = SupplierRepository(db)

    def _ensure_supplier(self, supplier_id: int) -> None:
        if self.suppliers.get_by_id(supplier_id) is None:
            raise BadRequestError(f"Supplier {supplier_id} does not exist")

    def _item_models(self, items: list[PurchaseOrderItemIn]) -> list[PurchaseOrderItem]:
        return [PurchaseOrderItem(**item.model_dump()) for item in items]

    def get(self, purchase_order_id: int) -> PurchaseOrder:
        purchase_order = self.repo.get_by_id(purchase_order_id)
        if purchase_order is None:
            raise NotFoundError(f"Purchase order {purchase_order_id} not found")
        return purchase_order

    def list(
        self,
        pagination: PaginationParams,
        status: str | None = None,
        supplier_id: int | None = None,
    ) -> tuple[list[PurchaseOrder], int]:
        return self.repo.list_paginated(
            pagination, self.repo.filtered_query(status=status, supplier_id=supplier_id)
        )

    def create(self, payload: PurchaseOrderCreate) -> PurchaseOrder:
        self._ensure_supplier(payload.supplier_id)
        entity = PurchaseOrder(
            supplier_id=payload.supplier_id,
            status=payload.status.value,
            expected_date=payload.expected_date,
            items=self._item_models(payload.items),
        )
        return self.repo.add(entity)

    def update(self, purchase_order_id: int, payload: PurchaseOrderUpdate) -> PurchaseOrder:
        purchase_order = self.get(purchase_order_id)
        data = payload.model_dump(exclude_unset=True)
        items = data.pop("items", None)
        if "supplier_id" in data:
            self._ensure_supplier(data["supplier_id"])
        if "status" in data and data["status"] is not None:
            data["status"] = payload.status.value if payload.status else data["status"]
        self.repo.apply_updates(purchase_order, data)
        if items is not None:
            self.repo.replace_items(purchase_order, self._item_models(payload.items or []))
        return self.get(purchase_order_id)

    def delete(self, purchase_order_id: int) -> None:
        try:
            self.repo.delete(self.get(purchase_order_id))
        except IntegrityError as exc:
            raise ConflictError("Cannot delete purchase order that has related invoices") from exc
