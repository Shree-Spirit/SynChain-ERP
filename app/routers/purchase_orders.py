from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import AuthContext, get_current_auth, require_admin
from app.db.session import get_db
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderRead,
    PurchaseOrderStatus,
    PurchaseOrderUpdate,
)
from app.services.purchase_order_service import PurchaseOrderService
from app.utils.pagination import PaginationParams, pagination_query

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.post("", response_model=PurchaseOrderRead, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    payload: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PurchaseOrderRead:
    return PurchaseOrderService(db).create(payload)


@router.get("", response_model=PaginatedResponse[PurchaseOrderRead])
def list_purchase_orders(
    status_filter: PurchaseOrderStatus | None = Query(default=None, alias="status"),
    supplier_id: int | None = Query(default=None),
    pagination: PaginationParams = Depends(pagination_query),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PaginatedResponse[PurchaseOrderRead]:
    items, total = PurchaseOrderService(db).list(
        pagination,
        status=status_filter.value if status_filter else None,
        supplier_id=supplier_id,
    )
    return PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size
    )


@router.get("/{purchase_order_id}", response_model=PurchaseOrderRead)
def get_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PurchaseOrderRead:
    return PurchaseOrderService(db).get(purchase_order_id)


@router.put("/{purchase_order_id}", response_model=PurchaseOrderRead)
def update_purchase_order(
    purchase_order_id: int,
    payload: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PurchaseOrderRead:
    return PurchaseOrderService(db).update(purchase_order_id, payload)


@router.delete("/{purchase_order_id}", response_model=MessageResponse)
def delete_purchase_order(
    purchase_order_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_admin),
) -> MessageResponse:
    PurchaseOrderService(db).delete(purchase_order_id)
    return MessageResponse(message="Purchase order deleted", id=purchase_order_id)
