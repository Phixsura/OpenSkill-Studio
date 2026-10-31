"""Support page — build support page with FAQ, contact, and docs links."""


def build_support_page(*, app: dict, faq: list[dict], contact: dict,
                          docs_url: str | None, community_url: str | None) -> dict:
    sections = []
    if faq:
        sections.append({"key": "faq", "title": f"FAQ ({len(faq)})", "icon": "❓", "items": faq})
    if docs_url:
        sections.append({"key": "docs", "title": "Documentation", "icon": "📚", "url": docs_url})
    if community_url:
        sections.append({"key": "community", "title": "Community", "icon": "💬", "url": community_url})
    sections.append({"key": "contact", "title": "Contact Developer", "icon": "📧",
                      "email": contact.get("email"), "response_time": contact.get("response_time", "2-3 business days")})
    return {
        "page_type": "app_support", "app_name": app["name"],
        "sections": sections, "section_count": len(sections),
        "has_faq": len(faq) > 0, "has_docs": docs_url is not None,
    }


def search_faq(*, faq: list[dict], query: str) -> list[dict]:
    q = query.lower()
    return [f for f in faq if q in f.get("question", "").lower() or q in f.get("answer", "").lower()]
