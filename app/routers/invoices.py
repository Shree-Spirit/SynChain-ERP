from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import AuthContext, get_current_auth, require_admin
from app.db.session import get_db
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.invoice import InvoiceCreate, InvoiceRead, InvoiceStatus, InvoiceUpdate
from app.services.invoice_service import InvoiceService
from app.utils.pagination import PaginationParams, pagination_query

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> InvoiceRead:
    return InvoiceService(db).create(payload)


@router.get("", response_model=PaginatedResponse[InvoiceRead])
def list_invoices(
    status_filter: InvoiceStatus | None = Query(default=None, alias="status"),
    order_id: int | None = Query(default=None),
    purchase_order_id: int | None = Query(default=None),
    pagination: PaginationParams = Depends(pagination_query),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PaginatedResponse[InvoiceRead]:
    items, total = InvoiceService(db).list(
        pagination,
        status=status_filter.value if status_filter else None,
        order_id=order_id,
        purchase_order_id=purchase_order_id,
    )
    return PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size
    )


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> InvoiceRead:
    return InvoiceService(db).get(invoice_id)


@router.put("/{invoice_id}", response_model=InvoiceRead)
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> InvoiceRead:
    return InvoiceService(db).update(invoice_id, payload)


@router.delete("/{invoice_id}", response_model=MessageResponse)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_admin),
) -> MessageResponse:
    InvoiceService(db).delete(invoice_id)
    return MessageResponse(message="Invoice deleted", id=invoice_id)
