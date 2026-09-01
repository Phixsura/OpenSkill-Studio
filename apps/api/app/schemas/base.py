import re as _re
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


_JSON_CTRL_RE = _re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def reject_ctrl_str(v, field_name: str):
    """Validator helper: reject NUL/control chars in a scalar string field.
    A NUL in a str written to a Postgres text/varchar column raises 22P05
    (UntranslatableCharacterError → DBAPIError, not ValueError) → 500."""
    if v is not None and _JSON_CTRL_RE.search(v):
        raise ValueError(f"{field_name} contains NUL or control characters that are not allowed")
    return v


def reject_ctrl_json(v, field_name: str):
    """Validator helper: reject NUL/control chars in ANY string nested in an
    open dict/list field. json.loads materializes a valid-JSON \\u0000 escape
    into a real NUL, which Postgres rejects on a JSONB write (22P05) as an
    UntranslatableCharacterError → DBAPIError (not ValueError) → 500. Scalar
    string fields use _reject_ctrl; open dict/list fields need this walk.
    Iterative (recursion-free) — the value may be deeply nested (already
    depth-capped separately, but this must not itself blow the stack)."""
    if v is None:
        return v
    stack = [v]
    while stack:
        cur = stack.pop()
        if isinstance(cur, str):
            if _JSON_CTRL_RE.search(cur):
                raise ValueError(
                    f"{field_name} contains NUL or control characters that are not allowed"
                )
        elif isinstance(cur, dict):
            stack.extend(cur.keys())
            stack.extend(cur.values())
        elif isinstance(cur, (list, tuple)):
            stack.extend(cur)
    return v


def reject_nonfinite_json(v, field_name: str):
    """Validator helper: reject NaN / Infinity / -Infinity floats anywhere in
    an open dict/list field. Stdlib json.loads (used by FastAPI request
    parsing) accepts the bare JSON tokens NaN/Infinity/-Infinity and yields
    real float('nan')/float('inf'), which pass every string/size/depth/ctrl
    check (those inspect str, not float). SQLAlchemy's default JSONB serializer
    is json.dumps with allow_nan=True, so it re-emits the literal `NaN`/
    `Infinity` token — which Postgres's jsonb parser rejects with 22P02
    (InvalidTextRepresentation → DBAPIError, not ValueError) → 500. bool is a
    subclass of int (not float) so it is unaffected; ints cannot be non-finite.
    Iterative (recursion-free) to match the depth-capped nested payloads."""
    import math

    if v is None:
        return v
    stack = [v]
    while stack:
        cur = stack.pop()
        if isinstance(cur, float):
            if not math.isfinite(cur):
                raise ValueError(
                    f"{field_name} contains NaN or Infinity values that are not allowed"
                )
        elif isinstance(cur, dict):
            stack.extend(cur.keys())
            stack.extend(cur.values())
        elif isinstance(cur, (list, tuple)):
            stack.extend(cur)
    return v


def safe_decimal(v, field_name: str):
    """Validator helper: parse a Decimal, mapping InvalidOperation to
    ValueError. decimal.InvalidOperation is an ArithmeticError — pydantic only
    wraps ValueError/AssertionError into 422s, so a raw Decimal('abc') in a
    field_validator escaped as an unhandled 500 (R58[34])."""
    from decimal import Decimal, InvalidOperation

    try:
        return Decimal(v)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"{field_name} must be a valid decimal number") from exc
