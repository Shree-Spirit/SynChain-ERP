from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import AuthContext, get_current_auth, require_admin
from app.db.session import get_db
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.inventory import InventoryItemCreate, InventoryItemRead, InventoryItemUpdate
from app.services.inventory_service import InventoryService
from app.utils.pagination import PaginationParams, pagination_query

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> InventoryItemRead:
    return InventoryService(db).create(payload)


@router.get("", response_model=PaginatedResponse[InventoryItemRead])
def list_inventory(
    warehouse_id: int | None = Query(default=None),
    sku: str | None = Query(default=None),
    name: str | None = Query(default=None),
    pagination: PaginationParams = Depends(pagination_query),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PaginatedResponse[InventoryItemRead]:
    items, total = InventoryService(db).list(
        pagination, warehouse_id=warehouse_id, sku=sku, name=name
    )
    return PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size
    )


@router.get("/{item_id}", response_model=InventoryItemRead)
def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> InventoryItemRead:
    return InventoryService(db).get(item_id)


@router.put("/{item_id}", response_model=InventoryItemRead)
def update_inventory_item(
    item_id: int,
    payload: InventoryItemUpdate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> InventoryItemRead:
    return InventoryService(db).update(item_id, payload)


@router.delete("/{item_id}", response_model=MessageResponse)
def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_admin),
) -> MessageResponse:
    InventoryService(db).delete(item_id)
    return MessageResponse(message="Inventory item deleted", id=item_id)
