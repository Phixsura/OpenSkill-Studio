"""Manifest validation service (ADR-016 Part J).

Server-side validation of app manifests that the CLI toolchain mirrors.
Checks schema compliance, permission validity, sandbox config bounds,
UI surface registration, and security constraints.
"""

import re

import structlog

log = structlog.get_logger()

# ── Valid permission scopes ──────────────────────────────

VALID_PERMISSIONS = frozenset({
    "read:organizations", "write:organizations",
    "read:members", "write:members",
    "read:cohorts", "write:cohorts", "read:cohort_members",
    "read:projects", "write:projects", "read:submissions", "write:project_results",
    "read:skills", "write:skills", "read:skill_progress",
    "read:packs", "write:packs", "read:installations",
    "read:workflows", "write:workflows", "read:workflow_runs", "write:workflow_runs",
    "read:providers", "write:providers", "read:credentials",
    "read:talent", "write:talent", "read:passports", "read:opportunities",
    "read:evaluations", "write:evaluations",
    "read:matching", "write:matching",
    "read:marketplace", "write:marketplace_listings",
    "subscribe:events",
    "extend:ui",
    "read:analytics", "export:analytics",
    "read:settings", "write:settings",
    "read:users", "read:user_profiles",
    "run:background_jobs",
})

VALID_SURFACES = frozenset({
    "dashboard_card", "project_sidebar", "cohort_tool",
    "submission_panel", "registry_detail", "settings_page",
    "client_portal_widget", "operator_console",
})

VALID_CATEGORIES = frozenset({
    "connector", "workflow_adapter", "ui_extension",
    "analytics", "automation", "content_pack", "ecosystem_source",
})

VALID_RUNTIMES = frozenset({
    "nodejs18", "nodejs20", "python3.11", "python3.12",
})

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$")

# Prohibited network destinations (name-based blocklist)
_BLOCKED_HOST_NAMES = frozenset({
    "localhost", "metadata.google.internal",
})
_BLOCKED_SUFFIXES = (".localhost", ".internal")


# ── Validation result ────────────────────────────────────


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


# ── Validator ────────────────────────────────────────────


def validate_manifest(manifest: dict) -> ValidationResult:
    """Validate an app manifest against the platform schema.

    Returns a ValidationResult with errors and warnings.
    """
    result = ValidationResult()

    if not isinstance(manifest, dict):
        result.error("Manifest must be a JSON object")
        return result

    # ── schema_version ───────────────────────────────────
    sv = manifest.get("schema_version")
    if not sv:
        result.error("Missing required field: schema_version")
    elif sv not in ("1.0", "1.1"):
        result.warn(f"Unknown schema_version '{sv}' — expected 1.0 or 1.1")

    # ── app block ────────────────────────────────────────
    app = manifest.get("app")
    if not isinstance(app, dict):
        result.error("Missing required field: app (object)")
    else:
        if not app.get("name"):
            result.error("app.name is required")
        elif len(app["name"]) > 100:
            result.error("app.name must be ≤100 characters")

        slug = app.get("slug")
        if slug and not re.match(r"^[a-z0-9][a-z0-9-]{0,58}[a-z0-9]$", slug):
            result.error("app.slug must be 2-60 lowercase alphanumeric with hyphens")

        version = app.get("version")
        if version and not SEMVER_RE.match(version):
            result.error(f"app.version '{version}' must follow semver (X.Y.Z)")

        category = app.get("category")
        if category and category not in VALID_CATEGORIES:
            result.error(f"app.category '{category}' is not valid. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}")

    # ── permissions ──────────────────────────────────────
    permissions = manifest.get("permissions")
    if permissions is not None:
        if not isinstance(permissions, list):
            result.error("permissions must be an array of strings")
        else:
            for perm in permissions:
                if not isinstance(perm, str):
                    result.error(f"permission must be a string, got {type(perm).__name__}")
                elif perm not in VALID_PERMISSIONS:
                    result.error(f"Unknown permission: '{perm}'")
            if len(permissions) > 50:
                result.error("Maximum 50 permissions allowed")
            if len(permissions) != len(set(permissions)):
                result.warn("Duplicate permissions detected")

    # ── sandbox config ───────────────────────────────────
    sandbox = manifest.get("sandbox")
    if isinstance(sandbox, dict):
        runtime = sandbox.get("runtime")
        if runtime and runtime not in VALID_RUNTIMES:
            result.warn(f"sandbox.runtime '{runtime}' is not a recognized runtime")

        memory_mb = sandbox.get("memory_mb")
        if memory_mb is not None:  # noqa: SIM102
            if not isinstance(memory_mb, int) or memory_mb < 32 or memory_mb > 512:
                result.error("sandbox.memory_mb must be 32-512")

        timeout_seconds = sandbox.get("timeout_seconds")
        if timeout_seconds is not None:  # noqa: SIM102
            if not isinstance(timeout_seconds, int) or timeout_seconds < 1 or timeout_seconds > 300:
                result.error("sandbox.timeout_seconds must be 1-300")

        network = sandbox.get("network")
        if isinstance(network, dict):
            allowed_hosts = network.get("allowed_hosts", [])
            for host in allowed_hosts:
                if not isinstance(host, str):
                    result.error(f"allowed_hosts entry must be a string, got {type(host).__name__}")
                    continue
                normalized = host.strip().rstrip(".").lower()
                if not normalized:
                    result.error("Empty host in allowed_hosts")
                    continue
                # Check name-based blocklist
                if normalized in _BLOCKED_HOST_NAMES or normalized.endswith(_BLOCKED_SUFFIXES):
                    result.error(f"Blocked network destination: '{host}' (internal)")
                    continue
                # Check IP-based blocklist
                import ipaddress
                try:
                    ip = ipaddress.ip_address(normalized)
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified or ip.is_multicast:
                        result.error(f"Blocked network destination: '{host}' (private/reserved IP)")
                except ValueError:
                    pass  # Not an IP — hostname is fine

            egress = network.get("egress_policy")
            if egress and egress not in ("allowlist", "deny_all"):
                result.warn(f"sandbox.network.egress_policy '{egress}' — expected 'allowlist' or 'deny_all'")

    # ── ui_extensions ────────────────────────────────────
    ui_ext = manifest.get("ui_extensions")
    if isinstance(ui_ext, list):
        if not manifest.get("permissions") or "extend:ui" not in manifest.get("permissions", []):
            result.warn("ui_extensions declared but 'extend:ui' permission not requested")

        for i, ext in enumerate(ui_ext):
            if not isinstance(ext, dict):
                result.error(f"ui_extensions[{i}] must be an object")
                continue
            surface = ext.get("surface")
            if not surface:
                result.error(f"ui_extensions[{i}].surface is required")
            elif surface not in VALID_SURFACES:
                result.error(f"ui_extensions[{i}].surface '{surface}' is not valid")

            if not ext.get("title"):
                result.error(f"ui_extensions[{i}].title is required")
            if not ext.get("entry"):
                result.error(f"ui_extensions[{i}].entry is required")

            viewport = ext.get("viewport")
            if isinstance(viewport, dict):
                w = viewport.get("width")
                h = viewport.get("height")
                if w is not None and (not isinstance(w, int) or w < 100 or w > 1920):
                    result.error(f"ui_extensions[{i}].viewport.width must be 100-1920")
                if h is not None and (not isinstance(h, int) or h < 100 or h > 1080):
                    result.error(f"ui_extensions[{i}].viewport.height must be 100-1080")

    # ── event_subscriptions ──────────────────────────────
    events = manifest.get("event_subscriptions")
    if isinstance(events, list):
        if not manifest.get("permissions") or "subscribe:events" not in manifest.get("permissions", []):
            result.warn("event_subscriptions declared but 'subscribe:events' permission not requested")

        for ev in events:
            if not isinstance(ev, str):
                result.error(f"event_subscription must be a string, got {type(ev).__name__}")

    # ── secrets ──────────────────────────────────────────
    secrets = manifest.get("secrets")
    if isinstance(secrets, list):
        keys_seen = set()
        for i, s in enumerate(secrets):
            if not isinstance(s, dict):
                result.error(f"secrets[{i}] must be an object")
                continue
            key = s.get("key")
            if not key:
                result.error(f"secrets[{i}].key is required")
            elif key in keys_seen:
                result.error(f"Duplicate secret key: '{key}'")
            else:
                keys_seen.add(key)
                if not re.match(r"^[A-Z][A-Z0-9_]{0,98}[A-Z0-9]$", key):
                    result.error(f"secrets[{i}].key '{key}' must be uppercase alphanumeric with underscores")

    # ── config_schema ────────────────────────────────────
    config_schema = manifest.get("config_schema")
    if isinstance(config_schema, dict) and config_schema.get("type") != "object":
        result.warn("config_schema.type should be 'object'")

    # ── Overall size check ───────────────────────────────
    import json
    manifest_size = len(json.dumps(manifest))
    if manifest_size > 500_000:
        result.error(f"Manifest too large: {manifest_size} bytes (max 500KB)")
    elif manifest_size > 100_000:
        result.warn(f"Large manifest: {manifest_size} bytes — consider reducing")

    return result
