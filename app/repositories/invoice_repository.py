from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Invoice)

    def filtered_query(
        self,
        status: str | None = None,
        order_id: int | None = None,
        purchase_order_id: int | None = None,
    ) -> Select:
        stmt = select(Invoice).order_by(Invoice.id)
        if status:
            stmt = stmt.where(Invoice.status == status)
        if order_id is not None:
            stmt = stmt.where(Invoice.order_id == order_id)
        if purchase_order_id is not None:
            stmt = stmt.where(Invoice.purchase_order_id == purchase_order_id)
        return stmt
