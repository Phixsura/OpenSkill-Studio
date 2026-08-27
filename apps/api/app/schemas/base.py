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


def max_json_depth(v, limit: int = 64) -> int:
    """Iterative max nesting depth of a JSON-ish value (recursion-free).

    json.loads parses far deeper (~900 levels in a 2KB payload) than
    pydantic's response serializer survives (~400) — an open dict/list field
    that stores a deep value poisons EVERY subsequent read of the row with
    PydanticSerializationError. Request validators cap depth at write time.
    Short-circuits once `limit` is exceeded (hostile payloads are wide AND
    deep — no need to walk the whole thing).
    """
    best = 1
    stack = [(v, 1)]
    while stack:
        cur, d = stack.pop()
        if d > best:
            best = d
            if best > limit:
                return best
        if isinstance(cur, dict):
            stack.extend((x, d + 1) for x in cur.values())
        elif isinstance(cur, (list, tuple)):
            stack.extend((x, d + 1) for x in cur)
    return best


def reject_deep_json(v, field_name: str, limit: int = 64):
    """Validator helper: raise ValueError when nesting exceeds `limit`."""
    if v is not None and max_json_depth(v, limit) > limit:
        raise ValueError(f"{field_name} is nested too deeply (max {limit} levels)")
    return v
