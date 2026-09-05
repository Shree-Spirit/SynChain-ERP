from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.utils.pagination import PaginationParams

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]) -> None:
        self.db = db
        self.model = model

    def get_by_id(self, record_id: int) -> ModelT | None:
        return self.db.get(self.model, record_id)

    def list_paginated(
        self,
        pagination: PaginationParams,
        statement: Select | None = None,
    ) -> tuple[list[ModelT], int]:
        stmt = statement if statement is not None else select(self.model)
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = self.db.scalar(count_stmt) or 0
        items = self.db.scalars(
            stmt.offset(pagination.offset).limit(pagination.page_size)
        ).all()
        return list(items), int(total)

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def apply_updates(self, instance: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            setattr(instance, key, value)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.db.delete(instance)
        self.db.flush()
