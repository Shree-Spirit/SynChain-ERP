from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Supplier)

    def filtered_query(self, name: str | None = None, category: str | None = None) -> Select:
        stmt = select(Supplier).order_by(Supplier.id)
        if name:
            stmt = stmt.where(Supplier.name.ilike(f"%{name}%"))
        if category:
            stmt = stmt.where(Supplier.category == category)
        return stmt
