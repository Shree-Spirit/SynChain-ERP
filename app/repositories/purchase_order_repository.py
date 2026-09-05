from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.repositories.base import BaseRepository


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, PurchaseOrder)

    def get_by_id(self, record_id: int) -> PurchaseOrder | None:
        return self.db.scalar(
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .where(PurchaseOrder.id == record_id)
        )

    def filtered_query(
        self,
        status: str | None = None,
        supplier_id: int | None = None,
    ) -> Select:
        stmt = (
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .order_by(PurchaseOrder.id)
        )
        if status:
            stmt = stmt.where(PurchaseOrder.status == status)
        if supplier_id is not None:
            stmt = stmt.where(PurchaseOrder.supplier_id == supplier_id)
        return stmt

    def replace_items(self, purchase_order: PurchaseOrder, items: list[PurchaseOrderItem]) -> None:
        purchase_order.items.clear()
        self.db.flush()
        purchase_order.items.extend(items)
        self.db.flush()
