from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    table_name: str
    record_id: int
    action: str
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    changed_by: str | None
    timestamp: datetime
