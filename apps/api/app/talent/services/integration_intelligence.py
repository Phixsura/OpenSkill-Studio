"""Integration intelligence — API keys, HRIS schema, ATS connectors, webhooks, Slack.

Closes gaps: #171-#180 (integration & API).
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime

# ---------------------------------------------------------------------------
# Gap #171: API key management
# ---------------------------------------------------------------------------

API_KEY_SCOPES = frozenset(
    {
        "read:capabilities",
        "write:capabilities",
        "read:evidence",
        "write:evidence",
        "read:passport",
        "write:passport",
        "read:opportunities",
        "write:opportunities",
        "read:applications",
        "write:applications",
        "read:analytics",
        "webhook:manage",
    }
)


@dataclass(frozen=True, slots=True)
class APIKey:
    id: str
    org_id: str
    name: str
    key_prefix: str  # first 8 chars shown, rest hashed
    key_hash: str
    scopes: list[str]
    expires_at: datetime | None
    created_by: str
    last_used_at: datetime | None


def generate_api_key(org_id: str, name: str, scopes: list[str]) -> dict:
    """Generate a new API key with prefix for display."""
    raw_key = f"osk_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return {
        "raw_key": raw_key,  # shown ONCE at creation
        "key_prefix": raw_key[:12],
        "key_hash": key_hash,
        "org_id": org_id,
        "name": name,
        "scopes": scopes,
    }


def validate_api_key_scopes(scopes: list[str]) -> list[str]:
    """Execute validate api key scopes."""
    errors = []
    invalid = set(scopes) - API_KEY_SCOPES
    if invalid:
        errors.append(f"Invalid scopes: {sorted(invalid)}. Valid: {sorted(API_KEY_SCOPES)}")
    if not scopes:
        errors.append("At least one scope is required")
    return errors


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """Verify an API key against its stored hash."""
    computed = hashlib.sha256(raw_key.encode()).hexdigest()
    return secrets.compare_digest(computed, stored_hash)


# ---------------------------------------------------------------------------
# Gap #173: HRIS integration schema
# ---------------------------------------------------------------------------

HRIS_EMPLOYEE_SCHEMA = {
    "type": "object",
    "required": ["employee_id", "first_name", "last_name", "email"],
    "properties": {
        "employee_id": {"type": "string", "description": "External HRIS employee ID"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "department": {"type": "string"},
        "job_title": {"type": "string"},
        "start_date": {"type": "string", "format": "date"},
        "end_date": {"type": "string", "format": "date", "nullable": True},
        "manager_id": {"type": "string", "nullable": True},
        "location": {"type": "string"},
        "employment_type": {
            "type": "string",
            "enum": ["full_time", "part_time", "contract", "intern"],
        },
        "status": {"type": "string", "enum": ["active", "inactive", "terminated"]},
    },
}

HRIS_JOB_SCHEMA = {
    "type": "object",
    "required": ["job_id", "title"],
    "properties": {
        "job_id": {"type": "string"},
        "title": {"type": "string"},
        "department": {"type": "string"},
        "description": {"type": "string"},
        "requirements": {"type": "array", "items": {"type": "string"}},
        "location": {"type": "string"},
        "employment_type": {"type": "string"},
        "compensation_range": {
            "type": "object",
            "properties": {
                "min": {"type": "number"},
                "max": {"type": "number"},
                "currency": {"type": "string"},
            },
        },
    },
}


SUPPORTED_HRIS_PROVIDERS = frozenset(
    {
        "workday",
        "bamboohr",
        "adp",
        "namely",
        "gusto",
        "rippling",
        "personio",
        "hibob",
        "sage",
        "custom",
    }
)


def validate_hris_employee(data: dict) -> list[str]:
    """Validate employee data against HRIS schema."""
    errors = []
    for field in HRIS_EMPLOYEE_SCHEMA["required"]:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    email = data.get("email", "")
    if email and "@" not in email:
        errors.append("Invalid email format")
    return errors


# ---------------------------------------------------------------------------
# Gap #174: ATS integration connectors
# ---------------------------------------------------------------------------

SUPPORTED_ATS_PROVIDERS = frozenset(
    {
        "greenhouse",
        "lever",
        "icims",
        "workable",
        "ashby",
        "teamtailor",
        "smartrecruiters",
        "custom",
    }
)


@dataclass(frozen=True, slots=True)
class ATSConnectorConfig:
    provider: str
    api_url: str
    api_key_encrypted: str
    sync_direction: str  # inbound, outbound, bidirectional
    sync_entities: list[str]  # jobs, candidates, applications, interviews
    last_sync_at: datetime | None


def validate_ats_config(config: dict) -> list[str]:
    """Execute validate ats config."""
    errors = []
    provider = config.get("provider", "")
    if provider not in SUPPORTED_ATS_PROVIDERS:
        errors.append(f"Unsupported ATS provider. Supported: {sorted(SUPPORTED_ATS_PROVIDERS)}")
    if not config.get("api_url"):
        errors.append("API URL is required")
    direction = config.get("sync_direction", "")
    if direction not in ("inbound", "outbound", "bidirectional"):
        errors.append("sync_direction must be inbound, outbound, or bidirectional")
    entities = config.get("sync_entities", [])
    valid_entities = {"jobs", "candidates", "applications", "interviews", "offers"}
    invalid = set(entities) - valid_entities
    if invalid:
        errors.append(f"Invalid sync entities: {sorted(invalid)}")
    return errors


# ---------------------------------------------------------------------------
# Gap #176: Slack/Teams notification schema
# ---------------------------------------------------------------------------

SLACK_EVENT_MAPPINGS = {
    "application.submitted": {
        "channel": "#hiring",
        "emoji": "📋",
        "template": "New application from {candidate} for {role}",
    },
    "application.stage_changed": {
        "channel": "#hiring",
        "emoji": "🔄",
        "template": "{candidate} moved to {stage} for {role}",
    },
    "offer.created": {
        "channel": "#hiring",
        "emoji": "🎉",
        "template": "Offer sent to {candidate} for {role}",
    },
    "placement.started": {
        "channel": "#hiring",
        "emoji": "🚀",
        "template": "{candidate} started at {role}",
    },
    "credential.issued": {
        "channel": "#achievements",
        "emoji": "🏆",
        "template": "{candidate} earned {credential}",
    },
}


def build_slack_message(event_type: str, context: dict) -> dict | None:
    """Build a Slack-formatted message for an event."""
    mapping = SLACK_EVENT_MAPPINGS.get(event_type)
    if not mapping:
        return None
    try:
        text = mapping["template"].format(**context)
    except KeyError:
        text = mapping["template"]
    return {
        "channel": mapping["channel"],
        "text": f"{mapping['emoji']} {text}",
        "event_type": event_type,
    }


def list_slack_event_mappings() -> list[str]:
    """Execute list slack event mappings."""
    return sorted(SLACK_EVENT_MAPPINGS.keys())


# ---------------------------------------------------------------------------
# Gap #178: Webhook signature verification endpoint
# ---------------------------------------------------------------------------


def build_verification_response(
    endpoint_id: str,
    public_key_info: str,
) -> dict:
    """Build response for webhook signature verification endpoint."""
    return {
        "endpoint_id": endpoint_id,
        "signing_algorithm": "HMAC-SHA256",
        "header_name": "X-OpenSkill-Signature",
        "verification_url": f"/api/v1/talent/webhooks/{endpoint_id}/verify",
        "public_key_info": public_key_info,
        "documentation_url": "https://docs.openskill.studio/webhooks/verification",
    }


# ---------------------------------------------------------------------------
# Gap #179: Per-endpoint rate limiting
# ---------------------------------------------------------------------------

ENDPOINT_RATE_LIMITS = {
    "POST /talent/capabilities/infer": {"limit": 20, "window_seconds": 60},
    "POST /talent/resume/parse": {"limit": 10, "window_seconds": 60},
    "POST /talent/capabilities/bulk": {"limit": 5, "window_seconds": 60},
    "POST /talent/applications/bulk-transition": {"limit": 10, "window_seconds": 60},
    "GET /talent/intelligence/*": {"limit": 30, "window_seconds": 60},
    "POST /talent/opportunities/*/match": {"limit": 10, "window_seconds": 60},
}


def get_endpoint_limit(method: str, path: str) -> dict | None:
    """Get rate limit config for a specific endpoint."""
    key = f"{method} {path}"
    if key in ENDPOINT_RATE_LIMITS:
        return ENDPOINT_RATE_LIMITS[key]
    # Check wildcard patterns
    for pattern, limit in ENDPOINT_RATE_LIMITS.items():
        if "*" in pattern:
            prefix = pattern.split("*")[0]
            if key.startswith(prefix.replace("*", "")):
                return limit
    return None
