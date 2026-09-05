from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.order import Order, OrderItem
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderItemIn, OrderUpdate
from app.utils.pagination import PaginationParams


class OrderService:
    def __init__(self, db: Session) -> None:
        self.repo = OrderRepository(db)

    def _item_models(self, items: list[OrderItemIn]) -> list[OrderItem]:
        return [OrderItem(**item.model_dump()) for item in items]

    def get(self, order_id: int) -> Order:
        order = self.repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        return order

    def list(
        self,
        pagination: PaginationParams,
        status: str | None = None,
        customer_name: str | None = None,
    ) -> tuple[list[Order], int]:
        return self.repo.list_paginated(
            pagination, self.repo.filtered_query(status=status, customer_name=customer_name)
        )

    def create(self, payload: OrderCreate) -> Order:
        entity = Order(
            customer_name=payload.customer_name,
            status=payload.status.value,
            order_date=payload.order_date,
            items=self._item_models(payload.items),
        )
        return self.repo.add(entity)

    def update(self, order_id: int, payload: OrderUpdate) -> Order:
        order = self.get(order_id)
        data = payload.model_dump(exclude_unset=True)
        items = data.pop("items", None)
        if "status" in data and payload.status is not None:
            data["status"] = payload.status.value
        self.repo.apply_updates(order, data)
        if items is not None:
            self.repo.replace_items(order, self._item_models(payload.items or []))
        return self.get(order_id)

    def delete(self, order_id: int) -> None:
        try:
            self.repo.delete(self.get(order_id))
        except IntegrityError as exc:
            raise ConflictError("Cannot delete order that has related invoices") from exc
