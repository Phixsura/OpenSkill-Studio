"""Developer certification — platform certification program for developers."""

import secrets
from datetime import datetime, timedelta


CERTIFICATIONS = {
    "platform_basics": {"label": "Platform Basics", "icon": "🎓", "required_score": 80, "questions": 20},
    "api_expert": {"label": "API Expert", "icon": "🔌", "required_score": 85, "questions": 30},
    "security_specialist": {"label": "Security Specialist", "icon": "🔒", "required_score": 90, "questions": 25},
    "marketplace_pro": {"label": "Marketplace Pro", "icon": "🏪", "required_score": 80, "questions": 25},
}


def take_exam(*, cert_id: str, score: int) -> dict:
    cert = CERTIFICATIONS.get(cert_id)
    if not cert:
        return {"error": f"Unknown certification. Valid: {', '.join(sorted(CERTIFICATIONS))}"}
    passed = score >= cert["required_score"]
    return {
        "cert_id": cert_id,
        "cert_label": cert["label"],
        "score": score,
        "required_score": cert["required_score"],
        "passed": passed,
        "certificate_id": f"cert_{secrets.token_urlsafe(12)}" if passed else None,
        "valid_until": (datetime.utcnow() + timedelta(days=365)).isoformat() if passed else None,
    }


def get_certification_progress(*, completed: list[str]) -> dict:
    total = len(CERTIFICATIONS)
    done = sum(1 for c in CERTIFICATIONS if c in completed)
    certs = []
    for cid, info in CERTIFICATIONS.items():
        certs.append({**info, "id": cid, "completed": cid in completed})
    return {"certifications": certs, "completed": done, "total": total,
            "progress_pct": round(done / total * 100)}
