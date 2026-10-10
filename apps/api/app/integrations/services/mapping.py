"""Bounded declarative mapping (ADR-018 §10).

The mapping DOCUMENT is structured config; only leaf `path` expressions use
JMESPath (not Turing-complete — boundable). Transforms come from a closed
in-repo registry. No tenant code ever executes (R83 invariant). The preview
endpoint runs the exact evaluator the engine uses — structural parity.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import jmespath
import structlog
from jmespath.exceptions import JMESPathError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models import (
    CANONICAL_MODELS,
    MAPPING_DIRECTIONS,
    MappingProfile,
)

log = structlog.get_logger()

MAX_FIELDS = 100
MAX_EXPR_LEN = 500
MAX_INPUT_BYTES = 262_144  # 256 KB per record
MAX_RESULT_DEPTH = 10
MAX_STRING_LEN = 10_000
MAX_PREVIEW_SAMPLES = 20


# ── transform registry (closed set; §10.2) ──


def _t_trim(v):
    return v.strip() if isinstance(v, str) else v


def _t_lower(v):
    return v.lower() if isinstance(v, str) else v


def _t_upper(v):
    return v.upper() if isinstance(v, str) else v


def _t_to_string(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _t_to_int(v):
    if v is None or isinstance(v, bool):
        raise _TransformError("not an integer")
    try:
        if isinstance(v, str) and v.strip() == "":
            return None
        out = int(str(v).strip())
    except (ValueError, TypeError) as exc:
        raise _TransformError("not an integer") from exc
    if not (-(2**53) < out < 2**53):
        raise _TransformError("integer out of range")
    return out


def _t_to_decimal(v):
    if v is None:
        return None
    try:
        d = Decimal(str(v).strip())
    except (InvalidOperation, ValueError) as exc:
        raise _TransformError("not a decimal") from exc
    if not d.is_finite():  # NaN/Infinity never reach JSONB (R87)
        raise _TransformError("non-finite decimal")
    return str(d)


def _t_date_iso(v):
    if v is None or v == "":
        return None
    s = str(v).strip()[:10]
    try:
        return date.fromisoformat(s).isoformat()
    except ValueError as exc:
        raise _TransformError("not an ISO date") from exc


def _t_datetime_iso(v):
    if v is None or v == "":
        return None
    try:
        return datetime.fromisoformat(str(v).strip().replace("Z", "+00:00")).isoformat()
    except ValueError as exc:
        raise _TransformError("not an ISO datetime") from exc


def _t_split_csv(v):
    if v is None or v == "":
        return []
    if isinstance(v, list):
        return v
    return [p.strip() for p in str(v).split(",") if p.strip()]


def _t_first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _t_coalesce_empty_null(v):
    return None if v in ("", [], {}) else v


TRANSFORMS = {
    "trim": _t_trim,
    "lower": _t_lower,
    "upper": _t_upper,
    "to_string": _t_to_string,
    "to_int": _t_to_int,
    "to_decimal": _t_to_decimal,
    "date_iso": _t_date_iso,
    "datetime_iso": _t_datetime_iso,
    "split_csv": _t_split_csv,
    "first": _t_first,
    "coalesce_empty_null": _t_coalesce_empty_null,
}


class _TransformError(Exception):
    pass


# ── document validation (at save time) ──


def validate_document(document: dict) -> list[str]:
    """Returns problems (empty = valid). Compiles every JMESPath expression
    so a bad one fails at save, never mid-run."""
    problems: list[str] = []
    fields = document.get("fields")
    if not isinstance(fields, list) or not fields:
        return ["document.fields: required non-empty list"]
    if len(fields) > MAX_FIELDS:
        return [f"document.fields: more than {MAX_FIELDS} fields"]
    seen_targets: set[str] = set()
    for i, f in enumerate(fields):
        where = f"fields[{i}]"
        if not isinstance(f, dict):
            problems.append(f"{where}: must be an object")
            continue
        unknown = set(f) - {"target", "path", "default", "enum_map", "enum_default", "transform"}
        if unknown:
            problems.append(f"{where}: unknown keys {sorted(unknown)}")
        target = f.get("target")
        if not isinstance(target, str) or not target or len(target) > 100:
            problems.append(f"{where}.target: required string")
        elif target in seen_targets:
            problems.append(f"{where}.target: duplicate {target!r}")
        else:
            seen_targets.add(target)
        path = f.get("path")
        if not isinstance(path, str) or not path or len(path) > MAX_EXPR_LEN:
            problems.append(f"{where}.path: required string <= {MAX_EXPR_LEN} chars")
        else:
            try:
                jmespath.compile(path)
            except JMESPathError as exc:
                problems.append(f"{where}.path: invalid JMESPath ({exc})")
        for name in f.get("transform", []) or []:
            if name not in TRANSFORMS:
                problems.append(f"{where}.transform: unknown transform {name!r}")
        enum_map = f.get("enum_map")
        if enum_map is not None:
            if not isinstance(enum_map, dict) or len(enum_map) > 200:
                problems.append(f"{where}.enum_map: must be an object (<=200 keys)")
            elif not all(
                isinstance(k, str) and isinstance(v, str | int | bool | float)
                for k, v in enum_map.items()
            ):
                problems.append(f"{where}.enum_map: scalar values only")
    return problems


# ── evaluation (engine + preview share this) ──


def _depth(value: Any, level: int = 0) -> int:
    if level > MAX_RESULT_DEPTH:
        return level
    if isinstance(value, dict):
        return max([level] + [_depth(v, level + 1) for v in value.values()])
    if isinstance(value, list):
        return max([level] + [_depth(v, level + 1) for v in value])
    return level


def apply_mapping(document: dict, record: dict) -> tuple[dict, list[dict]]:
    """Map one raw record. Returns (mapped, errors). An error entry is
    {"field": target, "code": ..., "message": ...}; any error means the
    record conflicts rather than half-applies."""
    if len(json.dumps(record, default=str)) > MAX_INPUT_BYTES:
        return {}, [{"field": "_record", "code": "input_too_large", "message": "record > 256KB"}]
    mapped: dict[str, Any] = {}
    errors: list[dict] = []
    for f in document.get("fields", []):
        target = f["target"]
        try:
            value = jmespath.search(f["path"], record)
        except JMESPathError:
            errors.append({"field": target, "code": "path_error", "message": "path failed"})
            continue
        if value is None and "default" in f:
            value = f["default"]
        for name in f.get("transform", []) or []:
            try:
                value = TRANSFORMS[name](value)
            except _TransformError as exc:
                errors.append({"field": target, "code": f"transform_{name}", "message": str(exc)})
                value = None
                break
        else:
            enum_map = f.get("enum_map")
            if enum_map is not None and value is not None:
                key = str(value)
                if key in enum_map:
                    value = enum_map[key]
                elif "enum_default" in f:
                    value = f["enum_default"]
                else:
                    errors.append(
                        {"field": target, "code": "enum_unmapped", "message": f"value {key!r}"}
                    )
                    continue
            if isinstance(value, str) and len(value) > MAX_STRING_LEN:
                errors.append({"field": target, "code": "too_long", "message": "string > 10k"})
                continue
            if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
                errors.append({"field": target, "code": "non_finite", "message": "NaN/Inf"})
                continue
            if _depth(value) >= MAX_RESULT_DEPTH:
                errors.append({"field": target, "code": "too_deep", "message": "depth > 10"})
                continue
            mapped[target] = value
    return mapped, errors


# ── profile CRUD ──


class MappingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        org_id: str,
        *,
        name: str,
        direction: str,
        model: str,
        document: dict,
        connection_id: str | None = None,
    ) -> MappingProfile:
        if direction not in MAPPING_DIRECTIONS:
            raise AppError("MAPPING_INVALID", "direction must be inbound|outbound", 422)
        if model not in CANONICAL_MODELS:
            raise AppError("MAPPING_INVALID", f"unknown canonical model: {model}", 422)
        problems = validate_document(document)
        if problems:
            raise AppError(
                "MAPPING_EXPRESSION_INVALID", "mapping document invalid", 422, details=problems
            )
        dup = (
            await self.db.execute(
                select(MappingProfile.id).where(
                    MappingProfile.org_id == org_id, MappingProfile.name == name
                )
            )
        ).scalar_one_or_none()
        if dup is not None:
            raise AppError("MAPPING_NAME_TAKEN", "A mapping with this name exists", 409)
        profile = MappingProfile(
            org_id=org_id,
            connection_id=connection_id,
            name=name,
            direction=direction,
            model=model,
            document=document,
        )
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def get(self, org_id: str, profile_id: str) -> MappingProfile:
        p = await self.db.get(MappingProfile, profile_id)
        if p is None or p.org_id != org_id:
            raise AppError("MAPPING_NOT_FOUND", "Mapping profile not found", 404)
        return p

    async def list(self, org_id: str) -> list[MappingProfile]:
        return list(
            (
                await self.db.execute(
                    select(MappingProfile)
                    .where(MappingProfile.org_id == org_id)
                    .order_by(MappingProfile.created_at)
                )
            ).scalars()
        )

    async def update_document(self, org_id: str, profile_id: str, document: dict) -> MappingProfile:
        p = await self.get(org_id, profile_id)
        problems = validate_document(document)
        if problems:
            raise AppError(
                "MAPPING_EXPRESSION_INVALID", "mapping document invalid", 422, details=problems
            )
        p.document = document
        p.version += 1  # pinned consumers keep the old shape until re-pinned
        await self.db.flush()
        return p

    async def preview(self, org_id: str, profile_id: str, samples: list[dict]) -> list[dict]:
        p = await self.get(org_id, profile_id)
        if len(samples) > MAX_PREVIEW_SAMPLES:
            raise AppError("MAPPING_PREVIEW_TOO_LARGE", "max 20 samples", 422)
        out = []
        for sample in samples:
            mapped, errors = apply_mapping(p.document, sample if isinstance(sample, dict) else {})
            out.append({"mapped": mapped, "errors": errors})
        return out
