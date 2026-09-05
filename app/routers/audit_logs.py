from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import AuthContext, get_current_auth
from app.db.session import get_db
from app.schemas.audit_log import AuditLogRead
from app.schemas.common import PaginatedResponse
from app.services.audit_log_service import AuditLogService
from app.utils.pagination import PaginationParams, pagination_query

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=PaginatedResponse[AuditLogRead])
def list_audit_logs(
    table_name: str | None = Query(default=None),
    record_id: int | None = Query(default=None),
    action: str | None = Query(default=None, description="CREATE, UPDATE, or DELETE"),
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
    pagination: PaginationParams = Depends(pagination_query),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PaginatedResponse[AuditLogRead]:
    items, total = AuditLogService(db).list(
        pagination,
        table_name=table_name,
        record_id=record_id,
        action=action,
        from_date=from_date,
        to_date=to_date,
    )
    return PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size
    )
