"""Cursor-based pagination for talent APIs.

Uses ULID cursor (time-ordered) instead of offset-based page/per_page.
Cursor = the ID of the last item in the previous page.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class CursorMeta(BaseModel):
    """Cursor pagination metadata."""

    next_cursor: str | None = None
    has_more: bool


class CursorListResponse(BaseModel, Generic[T]):
    """List response with cursor-based pagination."""

    data: list[T]
    meta: CursorMeta
