from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.invoice import Invoice
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.utils.pagination import PaginationParams


class InvoiceService:
    def __init__(self, db: Session) -> None:
        self.repo = InvoiceRepository(db)
        self.orders = OrderRepository(db)
        self.purchase_orders = PurchaseOrderRepository(db)

    def _validate_sources(
        self, order_id: int | None, purchase_order_id: int | None, require_one: bool = True
    ) -> None:
        if require_one and bool(order_id) == bool(purchase_order_id):
            raise BadRequestError("Provide exactly one of order_id or purchase_order_id")
        if order_id is not None and self.orders.get_by_id(order_id) is None:
            raise BadRequestError(f"Order {order_id} does not exist")
        if purchase_order_id is not None and self.purchase_orders.get_by_id(purchase_order_id) is None:
            raise BadRequestError(f"Purchase order {purchase_order_id} does not exist")

    def get(self, invoice_id: int) -> Invoice:
        invoice = self.repo.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundError(f"Invoice {invoice_id} not found")
        return invoice

    def list(
        self,
        pagination: PaginationParams,
        status: str | None = None,
        order_id: int | None = None,
        purchase_order_id: int | None = None,
    ) -> tuple[list[Invoice], int]:
        return self.repo.list_paginated(
            pagination,
            self.repo.filtered_query(
                status=status, order_id=order_id, purchase_order_id=purchase_order_id
            ),
        )

    def create(self, payload: InvoiceCreate) -> Invoice:
        self._validate_sources(payload.order_id, payload.purchase_order_id)
        try:
            return self.repo.add(
                Invoice(
                    order_id=payload.order_id,
                    purchase_order_id=payload.purchase_order_id,
                    amount=payload.amount,
                    status=payload.status.value,
                    due_date=payload.due_date,
                )
            )
        except IntegrityError as exc:
            raise BadRequestError("Invoice could not be created", str(exc.orig)) from exc

    def update(self, invoice_id: int, payload: InvoiceUpdate) -> Invoice:
        invoice = self.get(invoice_id)
        data = payload.model_dump(exclude_unset=True)
        order_id = data.get("order_id", invoice.order_id)
        purchase_order_id = data.get("purchase_order_id", invoice.purchase_order_id)
        if "order_id" in data or "purchase_order_id" in data:
            if "order_id" in data and data["order_id"] is not None:
                data["purchase_order_id"] = None
                purchase_order_id = None
            if "purchase_order_id" in data and data["purchase_order_id"] is not None:
                data["order_id"] = None
                order_id = None
            self._validate_sources(order_id, purchase_order_id)
        if "status" in data and payload.status is not None:
            data["status"] = payload.status.value
        try:
            return self.repo.apply_updates(invoice, data)
        except IntegrityError as exc:
            raise ConflictError("Invoice could not be updated") from exc

    def delete(self, invoice_id: int) -> None:
        self.repo.delete(self.get(invoice_id))
