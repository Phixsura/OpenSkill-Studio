"""Bulk CSV import pipeline (ADR-018 §16.1, research S8.3).

file -> validate (ALL errors collected, never first-error abort) ->
previewed -> commit (identical fingerprint or IMPORT_DRY_RUN_STALE).
Commit executes the SAME validation+write code path — parity is structural.
Modes: atomic (one txn, any error rolls everything back) and partial
(valid rows land, bad rows become row errors).

Template `users` v1: columns email (required), display_name, role
(student|instructor; org-mint ceiling as everywhere else). Idempotent by
email: matched-unchanged rows skip, drifted display_name updates,
re-uploads never duplicate.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from typing import Any

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.integrations.models.bulk import (
    IMPORT_KINDS,
    IMPORT_MODES,
    MAX_IMPORT_BYTES,
    MAX_ROW_ERRORS,
    ImportJob,
    ImportRowError,
)
from app.models.organization import MemberStatus, OrgMember, OrgRole
from app.models.user import User, UserRole, UserStatus

log = structlog.get_logger()

_EMAIL_RE = re.compile(r"[a-z0-9!#$%&'*/?^_`{|}~.+=-]+@[a-z0-9.-]+\.[a-z]{2,}")

TEMPLATE_VERSIONS = {"users": 1}
USERS_REQUIRED = ("email",)
USERS_OPTIONAL = ("display_name", "role")
IMPORT_ROLE_MAP = {"student": OrgRole.STUDENT, "instructor": OrgRole.INSTRUCTOR}


def fingerprint(file_bytes: bytes, template_version: int) -> str:
    h = hashlib.sha256()
    h.update(file_bytes)
    h.update(str(template_version).encode())
    return h.hexdigest()


def _sanitize_cell(value: str) -> str:
    """CSV-injection guard for the ERROR REPORT (S8.3): formula-leading
    cells get a quote prefix so Excel never executes them."""
    if value and value[0] in ("=", "+", "-", "@", "\t"):
        return "'" + value
    return value


def _validate_user_rows(
    raw_rows: list[tuple[int, dict]]
) -> tuple[list[dict], list[dict]]:
    """Shared user-row validation for every import format (R128). Input is
    (row_number, canonicalized-dict) pairs; output is (clean_rows, errors)
    with identical rules to the CSV path: valid email shape, NUL guard,
    role whitelist, in-file duplicate detection."""
    rows: list[dict] = []
    errors: list[dict] = []
    seen_emails: dict[str, int] = {}
    for i, row in raw_rows:
        email = str(row.get("email", "") or "").strip().lower()
        problems: list[tuple[str, str, str]] = []
        if (
            not email
            or len(email) > 255
            or "\x00" in email
            or not _EMAIL_RE.fullmatch(email)
        ):
            problems.append(("email", "invalid_email", "not a valid email address"))
        display = str(row.get("display_name", "") or "")[:100]
        if "\x00" in display:
            problems.append(("display_name", "control_chars", "NUL character"))
        role = str(row.get("role") or "student").lower()
        if role not in IMPORT_ROLE_MAP:
            problems.append(("role", "invalid_role", "role must be student|instructor"))
        if email and email in seen_emails:
            problems.append(
                ("email", "duplicate_in_file", f"also on row {seen_emails[email]}")
            )
        if problems:
            for col, code, message in problems:
                errors.append({
                    "row_number": i, "column": col, "code": code, "message": message,
                    "raw_row": {k: str(v)[:200] for k, v in row.items()},
                })
            continue
        seen_emails[email] = i
        rows.append({"row_number": i, "email": email, "display_name": display, "role": role})
    return rows, errors


def parse_users_json(
    file_bytes: bytes, header_map: dict | None = None
) -> tuple[list[dict], list[dict]]:
    """JSON users template (R128, Part K): a top-level list of objects, or
    {"users": [...]}. Same validation as CSV; header_map renames source keys
    to canonical. Row numbers are 1-indexed array positions."""
    import json as _json

    try:
        text = file_bytes.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return [], [{"row_number": 1, "code": "encoding", "message": "File is not UTF-8"}]
    try:
        doc = _json.loads(text or "null")
    except _json.JSONDecodeError:
        return [], [{"row_number": 1, "code": "invalid_json", "message": "File is not valid JSON"}]
    if isinstance(doc, dict):
        doc = doc.get("users")
    if not isinstance(doc, list):
        return [], [{"row_number": 1, "code": "invalid_shape",
                     "message": "expected a list of users or {\"users\": [...]}"}]
    alias = {str(k).strip().lower(): str(v).strip().lower() for k, v in (header_map or {}).items()}

    def _canon_obj(obj: dict) -> dict:
        out = {}
        for k, v in obj.items():
            key = str(k).strip().lower()
            # header_map for JSON maps canonical->source, so invert to find it.
            for canon, src in alias.items():
                if src == key:
                    key = canon
                    break
            out[key] = v
        return out

    raw_rows = []
    for idx, item in enumerate(doc, start=1):
        raw_rows.append((idx, _canon_obj(item) if isinstance(item, dict) else {}))
    return _validate_user_rows(raw_rows)


def parse_users(
    file_bytes: bytes, fmt: str, header_map: dict | None = None
) -> tuple[list[dict], list[dict]]:
    """Format dispatcher (R128)."""
    if fmt == "json":
        return parse_users_json(file_bytes, header_map)
    return parse_users_csv(file_bytes, header_map)


def detect_format(file_bytes: bytes) -> str:
    """R128: sniff JSON vs CSV by the first non-space byte (after BOM)."""
    head = file_bytes.lstrip(b"\xef\xbb\xbf \t\r\n")[:1]
    return "json" if head in (b"[", b"{") else "csv"


def parse_users_csv(
    file_bytes: bytes, header_map: dict | None = None
) -> tuple[list[dict], list[dict]]:
    """Streamed, header-based parse. Returns (rows, errors). Row numbers are
    1-indexed INCLUDING the header (user's spreadsheet view). BOM + CRLF
    tolerated; extra columns ignored; missing required column fails the file
    before any row is processed."""
    try:
        text = file_bytes.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return [], [{"row_number": 1, "code": "encoding", "message": "File is not UTF-8"}]
    reader = csv.DictReader(io.StringIO(text, newline=""))
    # R92 column mapping: {canonical: csv-header-alias}, case-insensitive on
    # the alias side. Unknown canonical keys are refused at create_job.
    alias_to_canonical = {
        str(v).strip().lower(): str(k).strip().lower()
        for k, v in (header_map or {}).items()
    }

    def _canon(header: str) -> str:
        h = header.strip().lower()
        return alias_to_canonical.get(h, h)

    headers = [_canon(h) for h in (reader.fieldnames or [])]
    missing = [c for c in USERS_REQUIRED if c not in headers]
    if missing:
        return [], [
            {
                "row_number": 1,
                "column": c,
                "code": "missing_column",
                "message": f"Required column {c!r} not found",
            }
            for c in missing
        ]
    raw_rows = []
    for i, raw in enumerate(reader, start=2):  # header is row 1
        raw_rows.append((i, {_canon(k or ""): (v or "").strip() for k, v in raw.items()
                             if k is not None}))
    return _validate_user_rows(raw_rows)


class BulkImportService:
    """``file_loader`` injection keeps S3 out of unit tests: the API layer
    stores the upload and loads by file_key; tests hand bytes directly."""

    def __init__(self, db: AsyncSession, file_loader=None):
        self.db = db
        self._load = file_loader

    # ── job lifecycle ──

    async def create_job(
        self,
        org_id: str,
        *,
        kind: str,
        mode: str,
        file_bytes: bytes,
        file_key: str,
        created_by: str,
        idempotency_key: str | None = None,
        header_map: dict | None = None,
    ) -> ImportJob:
        if kind not in IMPORT_KINDS:
            raise AppError("IMPORT_KIND_INVALID", f"kind must be one of {sorted(IMPORT_KINDS)}", 422)
        if mode not in IMPORT_MODES:
            raise AppError("IMPORT_MODE_INVALID", "mode must be atomic|partial", 422)
        if len(file_bytes) > MAX_IMPORT_BYTES:
            raise AppError("IMPORT_TOO_LARGE", "file exceeds 50MB", 422)
        header_map = header_map or {}
        if len(header_map) > 20:
            raise AppError("IMPORT_HEADER_MAP_INVALID", "too many mappings", 422)
        known = {"email", "display_name", "role"}
        for k, v in header_map.items():
            if str(k).strip().lower() not in known or not isinstance(v, str) or not v.strip():
                raise AppError(
                    "IMPORT_HEADER_MAP_INVALID",
                    f"header_map keys must be in {sorted(known)} with string aliases",
                    422,
                )
        if idempotency_key:
            existing = (
                await self.db.execute(
                    select(ImportJob).where(
                        ImportJob.org_id == org_id,
                        ImportJob.idempotency_key == idempotency_key,
                    )
                )
            ).scalar_one_or_none()
            if existing is not None:
                return existing  # idempotent re-upload returns the same job
        version = TEMPLATE_VERSIONS[kind]
        job = ImportJob(
            org_id=org_id,
            kind=kind,
            template_version=version,
            mode=mode,
            file_key=file_key,
            fingerprint=fingerprint(file_bytes, version),
            created_by=created_by,
            idempotency_key=idempotency_key,
            header_map=header_map,
        )
        self.db.add(job)
        await self.db.flush()
        await self._validate(job, file_bytes)
        await self.db.refresh(job)
        return job

    async def _validate(self, job: ImportJob, file_bytes: bytes) -> None:
        rows, errors = parse_users(file_bytes, detect_format(file_bytes), job.header_map or {})
        creates = updates = skips = 0
        for row in rows:
            user = (
                await self.db.execute(
                    select(User).where(func.lower(User.email) == row["email"])
                )
            ).scalar_one_or_none()
            if user is None:
                creates += 1
                continue
            member = (
                await self.db.execute(
                    select(OrgMember).where(
                        OrgMember.org_id == job.org_id, OrgMember.user_id == user.id
                    )
                )
            ).scalar_one_or_none()
            if member is None or (
                row["display_name"] and row["display_name"] != user.display_name
            ):
                updates += 1
            else:
                skips += 1
        for e in errors[:MAX_ROW_ERRORS]:
            self.db.add(
                ImportRowError(
                    job_id=job.id,
                    row_number=e["row_number"],
                    column=e.get("column"),
                    code=e["code"],
                    message=e["message"],
                    raw_row=e.get("raw_row", {}),
                )
            )
        job.dry_stats = {
            "valid": len(rows),
            "errors": len(errors),
            "creates": creates,
            "updates": updates,
            "skips": skips,
        }
        job.status = "previewed"
        await self.db.flush()

    async def get(self, org_id: str, job_id: str) -> ImportJob:
        job = await self.db.get(ImportJob, job_id)
        if job is None or job.org_id != org_id:
            raise AppError("IMPORT_NOT_FOUND", "Import job not found", 404)
        return job

    async def commit(self, org_id: str, job_id: str, *, file_bytes: bytes) -> ImportJob:
        job = await self.get(org_id, job_id)
        if fingerprint(file_bytes, job.template_version) != job.fingerprint:
            raise AppError(
                "IMPORT_DRY_RUN_STALE",
                "File changed since the preview — re-upload and preview again",
                409,
            )
        # Atomic claim (review defect #5): two concurrent commits must not
        # both apply — only the UPDATE winner proceeds.
        from sqlalchemy import update as _update

        claimed = (
            await self.db.execute(
                _update(ImportJob)
                .where(ImportJob.id == job.id, ImportJob.status == "previewed")
                .values(status="committing")
                .returning(ImportJob.id)
            )
        ).scalar_one_or_none()
        if claimed is None:
            raise AppError("IMPORT_NOT_COMMITTABLE", f"job is {job.status}", 409)
        await self.db.refresh(job)
        rows, errors = parse_users(file_bytes, detect_format(file_bytes), job.header_map or {})
        if job.mode == "atomic" and errors:
            job.status = "failed"
            job.stats = {"applied": 0, "errors": len(errors), "reason": "atomic_reject"}
            await self.db.flush()
            return job

        applied = created = updated = skipped = 0
        row_failures = 0
        for row in rows:
            try:
                async with self.db.begin_nested():
                    outcome = await self._apply_row(job.org_id, row)
            except Exception as exc:  # row-level failure
                row_failures += 1
                if job.mode == "atomic":
                    job.status = "failed"
                    job.stats = {
                        "applied": 0,
                        "errors": row_failures,
                        "reason": f"row_{row['row_number']}:{type(exc).__name__}",
                    }
                    await self.db.flush()
                    raise AppError(
                        "IMPORT_FAILED", "Atomic import failed; nothing was applied", 422
                    ) from exc
                self.db.add(
                    ImportRowError(
                        job_id=job.id,
                        row_number=row["row_number"],
                        column=None,
                        code="apply_failed",
                        message=str(exc)[:300],
                        raw_row={"email": row["email"]},
                    )
                )
                continue
            applied += 1
            created += outcome == "created"
            updated += outcome == "updated"
            skipped += outcome == "skipped"
        job.stats = {
            "applied": applied,
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "errors": len(errors) + row_failures,
        }
        job.status = (
            "succeeded" if not errors and not row_failures else "partial"
        )
        await self.db.flush()
        return job

    async def _apply_row(self, org_id: str, row: dict) -> str:
        user = (
            await self.db.execute(
                select(User).where(func.lower(User.email) == row["email"])
            )
        ).scalar_one_or_none()
        outcome = "skipped"
        if user is None:
            user = User(
                email=row["email"],
                password_hash=None,
                display_name=row["display_name"] or row["email"].split("@", 1)[0],
                role=UserRole.STUDENT,
                status=UserStatus.ACTIVE,
                email_verified=False,  # imported, not IdP-verified
            )
            self.db.add(user)
            await self.db.flush()
            outcome = "created"
        elif row["display_name"] and row["display_name"] != user.display_name:
            user.display_name = row["display_name"]
            outcome = "updated"
        member = (
            await self.db.execute(
                select(OrgMember).where(
                    OrgMember.org_id == org_id, OrgMember.user_id == user.id
                )
            )
        ).scalar_one_or_none()
        if member is None:
            self.db.add(
                OrgMember(
                    org_id=org_id,
                    user_id=user.id,
                    role=IMPORT_ROLE_MAP[row["role"]],
                    status=MemberStatus.ACTIVE,
                )
            )
            outcome = "created" if outcome == "created" else "updated"
        elif member.status != MemberStatus.ACTIVE:
            member.status = MemberStatus.ACTIVE
            outcome = "updated"
        # Role is NEVER changed for existing members (human decisions win —
        # same rule as roster role_conflict; the import only sets initial role).
        await self.db.flush()
        return outcome

    # ── error report ──

    async def errors_csv(self, org_id: str, job_id: str) -> str:
        job = await self.get(org_id, job_id)
        rows = (
            await self.db.execute(
                select(ImportRowError)
                .where(ImportRowError.job_id == job.id)
                .order_by(ImportRowError.row_number)
            )
        ).scalars().all()
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["row_number", "column", "code", "message", "email"])
        for r in rows:
            raw: dict[str, Any] = r.raw_row or {}
            writer.writerow(
                [
                    r.row_number,
                    _sanitize_cell(r.column or ""),
                    _sanitize_cell(r.code),
                    _sanitize_cell(r.message),
                    _sanitize_cell(str(raw.get("email", ""))),
                ]
            )
        return buf.getvalue()
