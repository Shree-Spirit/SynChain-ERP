from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryItem]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, InventoryItem)

    def get_by_sku(self, sku: str) -> InventoryItem | None:
        return self.db.scalar(select(InventoryItem).where(InventoryItem.sku == sku))

    def filtered_query(
        self,
        warehouse_id: int | None = None,
        sku: str | None = None,
        name: str | None = None,
    ) -> Select:
        stmt = select(InventoryItem).order_by(InventoryItem.id)
        if warehouse_id is not None:
            stmt = stmt.where(InventoryItem.warehouse_id == warehouse_id)
        if sku:
            stmt = stmt.where(InventoryItem.sku.ilike(f"%{sku}%"))
        if name:
            stmt = stmt.where(InventoryItem.name.ilike(f"%{name}%"))
        return stmt
