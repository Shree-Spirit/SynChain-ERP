from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository
from app.utils.pagination import PaginationParams


class AuditLogService:
    def __init__(self, db: Session) -> None:
        self.repo = AuditLogRepository(db)

    def list(
        self,
        pagination: PaginationParams,
        table_name: str | None = None,
        record_id: int | None = None,
        action: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> tuple[list[AuditLog], int]:
        return self.repo.list_paginated(
            pagination,
            self.repo.filtered_query(
                table_name=table_name,
                record_id=record_id,
                action=action,
                from_date=from_date,
                to_date=to_date,
            ),
        )
