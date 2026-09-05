from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import AuthContext, get_current_auth, require_admin
from app.db.session import get_db
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.order import OrderCreate, OrderRead, OrderStatus, OrderUpdate
from app.services.order_service import OrderService
from app.utils.pagination import PaginationParams, pagination_query

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> OrderRead:
    return OrderService(db).create(payload)


@router.get("", response_model=PaginatedResponse[OrderRead])
def list_orders(
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    customer_name: str | None = Query(default=None),
    pagination: PaginationParams = Depends(pagination_query),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PaginatedResponse[OrderRead]:
    items, total = OrderService(db).list(
        pagination,
        status=status_filter.value if status_filter else None,
        customer_name=customer_name,
    )
    return PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size
    )


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> OrderRead:
    return OrderService(db).get(order_id)


@router.put("/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> OrderRead:
    return OrderService(db).update(order_id, payload)


@router.delete("/{order_id}", response_model=MessageResponse)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_admin),
) -> MessageResponse:
    OrderService(db).delete(order_id)
    return MessageResponse(message="Order deleted", id=order_id)
