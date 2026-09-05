from contextvars import ContextVar
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import event, inspect
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper

from app.models.audit_log import AuditLog
from app.models.inventory import InventoryItem
from app.models.invoice import Invoice
from app.models.order import Order, OrderItem
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse

_current_actor: ContextVar[str] = ContextVar("current_actor", default="system")

_LISTENERS_REGISTERED = False

AUDITED_MODELS = (
    Supplier,
    Warehouse,
    InventoryItem,
    PurchaseOrder,
    PurchaseOrderItem,
    Order,
    OrderItem,
    Invoice,
)


def set_current_actor(actor: str) -> None:
    _current_actor.set(actor)


def get_current_actor() -> str:
    return _current_actor.get()


def serialize_instance(obj: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    mapper = inspect(obj).mapper
    for column in mapper.column_attrs:
        value = getattr(obj, column.key)
        data[column.key] = _json_safe(value)
    return data


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    return value


def _changed_columns(obj: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    old: dict[str, Any] = {}
    new: dict[str, Any] = {}
    state = inspect(obj)
    for attr in state.mapper.column_attrs:
        history = state.attrs[attr.key].history
        if not history.has_changes():
            continue
        old[attr.key] = _json_safe(history.deleted[0] if history.deleted else None)
        new[attr.key] = _json_safe(history.added[0] if history.added else getattr(obj, attr.key))
    return old, new


def _write_audit(
    connection: Connection,
    table_name: str,
    record_id: int,
    action: str,
    old_value: dict[str, Any] | None,
    new_value: dict[str, Any] | None,
) -> None:
    connection.execute(
        AuditLog.__table__.insert().values(
            table_name=table_name,
            record_id=record_id or 0,
            action=action,
            old_value=old_value,
            new_value=new_value,
            changed_by=get_current_actor(),
        )
    )


def _after_insert(mapper: Mapper, connection: Connection, target: Any) -> None:
    _write_audit(
        connection,
        target.__tablename__,
        getattr(target, "id", 0),
        "CREATE",
        None,
        serialize_instance(target),
    )


def _after_update(mapper: Mapper, connection: Connection, target: Any) -> None:
    old_value, new_value = _changed_columns(target)
    if not old_value and not new_value:
        return
    _write_audit(
        connection,
        target.__tablename__,
        getattr(target, "id", 0),
        "UPDATE",
        old_value,
        new_value,
    )


def _after_delete(mapper: Mapper, connection: Connection, target: Any) -> None:
    _write_audit(
        connection,
        target.__tablename__,
        getattr(target, "id", 0),
        "DELETE",
        serialize_instance(target),
        None,
    )


def register_audit_listeners() -> None:
    global _LISTENERS_REGISTERED
    if _LISTENERS_REGISTERED:
        return
    _LISTENERS_REGISTERED = True
    for model in AUDITED_MODELS:
        event.listen(model, "after_insert", _after_insert)
        event.listen(model, "after_update", _after_update)
        event.listen(model, "after_delete", _after_delete)
