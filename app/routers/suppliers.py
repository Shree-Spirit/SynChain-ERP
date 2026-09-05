from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import AuthContext, get_current_auth, require_admin
from app.db.session import get_db
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate
from app.services.supplier_service import SupplierService
from app.utils.pagination import PaginationParams, pagination_query

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> SupplierRead:
    return SupplierService(db).create(payload)


@router.get("", response_model=PaginatedResponse[SupplierRead])
def list_suppliers(
    name: str | None = Query(default=None),
    category: str | None = Query(default=None),
    pagination: PaginationParams = Depends(pagination_query),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> PaginatedResponse[SupplierRead]:
    items, total = SupplierService(db).list(pagination, name=name, category=category)
    return PaginatedResponse(
        items=items, total=total, page=pagination.page, page_size=pagination.page_size
    )


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> SupplierRead:
    return SupplierService(db).get(supplier_id)


@router.put("/{supplier_id}", response_model=SupplierRead)
def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_current_auth),
) -> SupplierRead:
    return SupplierService(db).update(supplier_id, payload)


@router.delete("/{supplier_id}", response_model=MessageResponse)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_admin),
) -> MessageResponse:
    SupplierService(db).delete(supplier_id)
    return MessageResponse(message="Supplier deleted", id=supplier_id)
