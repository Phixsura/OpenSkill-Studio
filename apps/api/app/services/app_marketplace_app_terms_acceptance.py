"""Terms acceptance — track ToS and privacy policy acceptance."""

from datetime import datetime
import hashlib


def get_current_terms(*, document_type: str = "tos") -> dict:
    docs = {
        "tos": {"version": "2.1", "title": "Terms of Service",
                "effective_date": "2026-09-01", "url": "https://openskill.dev/legal/tos"},
        "privacy": {"version": "1.5", "title": "Privacy Policy",
                     "effective_date": "2026-08-15", "url": "https://openskill.dev/legal/privacy"},
        "dpa": {"version": "1.0", "title": "Data Processing Agreement",
                "effective_date": "2026-07-01", "url": "https://openskill.dev/legal/dpa"},
    }
    doc = docs.get(document_type)
    if not doc:
        return {"error": f"Unknown document. Valid: {', '.join(docs)}"}
    return {"document_type": document_type, **doc}


def record_acceptance(*, user_id: str, document_type: str, version: str,
                        ip_address: str | None = None) -> dict:
    sig = hashlib.sha256(f"{user_id}:{document_type}:{version}".encode()).hexdigest()[:16]
    return {
        "acceptance_id": f"acc_{sig}",
        "user_id": user_id,
        "document_type": document_type,
        "version": version,
        "accepted_at": datetime.utcnow().isoformat(),
        "ip_address": ip_address,
    }


def check_acceptance(*, user_acceptances: list[dict], required: list[dict]) -> dict:
    accepted_map = {(a["document_type"], a["version"]): True for a in user_acceptances}
    pending = []
    for req in required:
        key = (req["document_type"], req["version"])
        if key not in accepted_map:
            pending.append(req)
    return {"all_accepted": len(pending) == 0, "pending": pending,
            "pending_count": len(pending)}
