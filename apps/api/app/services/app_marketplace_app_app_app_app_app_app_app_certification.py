"""Developer certification — track certification progress and issue badges."""
from __future__ import annotations

CERTIFICATIONS = {
    "platform_basics": {"title": "Platform Basics", "icon": "📘", "modules": 5, "passing_score": 80},
    "api_expert": {"title": "API Expert", "icon": "🔧", "modules": 8, "passing_score": 85},
    "security_specialist": {"title": "Security Specialist", "icon": "🔒", "modules": 6, "passing_score": 90},
    "marketplace_publisher": {"title": "Marketplace Publisher", "icon": "🏪", "modules": 4, "passing_score": 80},
}


def get_certification(cert_id: str) -> dict | None:
    c = CERTIFICATIONS.get(cert_id)
    if not c:
        return None
    return {"id": cert_id, **c}


def evaluate_exam(cert_id: str, *, score: int, modules_completed: int) -> dict:
    cert = CERTIFICATIONS.get(cert_id)
    if not cert:
        return {"error": "Certification not found"}
    passed = score >= cert["passing_score"] and modules_completed >= cert["modules"]
    return {"cert_id": cert_id, "title": cert["title"], "score": score,
            "passing_score": cert["passing_score"],
            "modules_completed": modules_completed, "modules_required": cert["modules"],
            "passed": passed, "icon": cert["icon"],
            "badge": f"Certified {cert['title']}" if passed else None}


def list_certifications() -> list[dict]:
    return [{"id": k, **v} for k, v in CERTIFICATIONS.items()]
