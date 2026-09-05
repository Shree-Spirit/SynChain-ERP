from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import AuthContext, get_current_auth, require_admin
from app.db.session import get_db
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.services.warehouse_service import WarehouseService
from app.utils.pagination import PaginationParams, pagination_query

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    payload: WarehouseCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> WarehouseRead:
    return WarehouseService(db).create(payload)


@router.get("", response_model=PaginatedResponse[WarehouseRead])
def list_warehouses(
    location: str | None = Query(default=None),
    name: str | None = Query(default=None),
    pagination: PaginationParams = Depends(pagination_query),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PaginatedResponse[WarehouseRead]:
    items, total = WarehouseService(db).list(pagination, location=location, name=name)
    return PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size
    )


@router.get("/{warehouse_id}", response_model=WarehouseRead)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> WarehouseRead:
    return WarehouseService(db).get(warehouse_id)


@router.put("/{warehouse_id}", response_model=WarehouseRead)
def update_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> WarehouseRead:
    return WarehouseService(db).update(warehouse_id, payload)


@router.delete("/{warehouse_id}", response_model=MessageResponse)
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_admin),
) -> MessageResponse:
    WarehouseService(db).delete(warehouse_id)
    return MessageResponse(message="Warehouse deleted", id=warehouse_id)
