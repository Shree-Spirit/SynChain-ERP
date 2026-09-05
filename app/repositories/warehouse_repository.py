from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse
from app.repositories.base import BaseRepository


class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Warehouse)

    def filtered_query(self, location: str | None = None, name: str | None = None) -> Select:
        stmt = select(Warehouse).order_by(Warehouse.id)
        if location:
            stmt = stmt.where(Warehouse.location.ilike(f"%{location}%"))
        if name:
            stmt = stmt.where(Warehouse.name.ilike(f"%{name}%"))
        return stmt
