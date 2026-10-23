"""Developer newsletter — automated newsletter generation from platform activity."""

from datetime import datetime, timezone


def generate_newsletter(*, period: str, new_apps: list[dict], trending: list[dict],
                           announcements: list[str], tips: list[str]) -> dict:
    sections = []
    if announcements:
        sections.append({"title": "📢 Announcements", "items": announcements})
    if new_apps:
        sections.append({"title": "🆕 New Apps", "items": [f"{a['name']} — {a.get('description', '')}" for a in new_apps[:5]]})
    if trending:
        sections.append({"title": "🔥 Trending", "items": [a["name"] for a in trending[:5]]})
    if tips:
        sections.append({"title": "💡 Developer Tips", "items": tips})
    return {"period": period, "sections": sections, "section_count": len(sections),
            "generated_at": datetime.now(timezone.utc).isoformat()}


def build_email_subject(*, period: str, highlight: str | None = None) -> str:
    base = f"OpenSkill Developer Update — {period}"
    return f"{base}: {highlight}" if highlight else base
