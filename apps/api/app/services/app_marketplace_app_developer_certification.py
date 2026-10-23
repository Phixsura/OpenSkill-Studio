"""Developer certification — badge and certification program for developers."""

CERTIFICATIONS = {
    "marketplace_basics": {"title": "Marketplace Basics", "requirements": 3, "badge": "🎓"},
    "security_expert": {"title": "Security Expert", "requirements": 5, "badge": "🔒"},
    "integration_master": {"title": "Integration Master", "requirements": 7, "badge": "🔗"},
    "top_publisher": {"title": "Top Publisher", "requirements": 10, "badge": "⭐"},
}


def check_certification(*, cert_id: str, completed_tasks: int) -> dict:
    cert = CERTIFICATIONS.get(cert_id)
    if not cert:
        return {"error": f"Unknown certification: {cert_id}"}
    earned = completed_tasks >= cert["requirements"]
    return {"certification": cert["title"], "badge": cert["badge"],
            "earned": earned, "progress": min(completed_tasks, cert["requirements"]),
            "required": cert["requirements"],
            "pct": round(min(completed_tasks, cert["requirements"]) / cert["requirements"] * 100)}


def get_developer_badges(*, completed_certs: list[str]) -> list[dict]:
    return [{"id": c, **CERTIFICATIONS[c]} for c in completed_certs if c in CERTIFICATIONS]


def list_available_certifications() -> list[dict]:
    return [{"id": k, **v} for k, v in CERTIFICATIONS.items()]
