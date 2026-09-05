from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class MessageResponse(BaseModel):
    message: str
    id: int | None = None


class ErrorResponse(BaseModel):
    status_code: int
    message: str
    detail: str | dict | list | None = None
