from typing import TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def pagination_query(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
