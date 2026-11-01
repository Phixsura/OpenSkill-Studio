"""Consent manager — GDPR/privacy consent tracking."""

import html
import secrets
from datetime import datetime, timezone

CONSENT_TYPES = {
    "essential": {"required": True, "description": "Required for app functionality"},
    "analytics": {"required": False, "description": "Usage analytics and metrics"},
    "marketing": {"required": False, "description": "Marketing communications"},
    "third_party": {"required": False, "description": "Third-party integrations"},
}


def build_consent_form(*, current: dict[str, bool] | None = None) -> dict:
    items = []
    for ctype, info in CONSENT_TYPES.items():
        granted = current.get(ctype, info["required"]) if current else info["required"]
        items.append({"type": ctype, "description": info["description"],
                       "required": info["required"], "granted": granted,
                       "editable": not info["required"]})
    return {"items": items, "total": len(items),
            "all_granted": all(i["granted"] for i in items)}


def record_consent(*, user_id: str, consents: dict[str, bool]) -> dict:
    record_id = f"consent_{secrets.token_hex(8)}"
    final = {}
    for ctype, info in CONSENT_TYPES.items():
        if info["required"]:
            final[ctype] = True
        else:
            final[ctype] = consents.get(ctype, False)
    return {"id": record_id, "user_id": user_id, "consents": final,
            "recorded_at": datetime.now(timezone.utc).isoformat()}
