from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class DataResponse(BaseModel, Generic[T]):
    """Single resource response."""

    data: T


class ListResponse(BaseModel, Generic[T]):
    """List response with pagination."""

    data: list[T]
    meta: "PaginationMeta"


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    has_more: bool


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[Any] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
