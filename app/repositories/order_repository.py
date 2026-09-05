from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order, OrderItem
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Order)

    def get_by_id(self, record_id: int) -> Order | None:
        return self.db.scalar(
            select(Order).options(selectinload(Order.items)).where(Order.id == record_id)
        )

    def filtered_query(
        self,
        status: str | None = None,
        customer_name: str | None = None,
    ) -> Select:
        stmt = select(Order).options(selectinload(Order.items)).order_by(Order.id)
        if status:
            stmt = stmt.where(Order.status == status)
        if customer_name:
            stmt = stmt.where(Order.customer_name.ilike(f"%{customer_name}%"))
        return stmt

    def replace_items(self, order: Order, items: list[OrderItem]) -> None:
        order.items.clear()
        self.db.flush()
        order.items.extend(items)
        self.db.flush()
