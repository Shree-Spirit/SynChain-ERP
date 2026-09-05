from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, AuditLog)

    def filtered_query(
        self,
        table_name: str | None = None,
        record_id: int | None = None,
        action: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> Select:
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
        if table_name:
            stmt = stmt.where(AuditLog.table_name == table_name)
        if record_id is not None:
            stmt = stmt.where(AuditLog.record_id == record_id)
        if action:
            stmt = stmt.where(AuditLog.action == action.upper())
        if from_date:
            stmt = stmt.where(AuditLog.timestamp >= from_date)
        if to_date:
            stmt = stmt.where(AuditLog.timestamp <= to_date)
        return stmt
