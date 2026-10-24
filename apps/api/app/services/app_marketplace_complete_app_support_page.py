"""Complete app support page — support center with FAQ, tickets, and docs."""


def build_complete_support_page(*, app: dict, faq: list[dict], open_tickets: list[dict],
                                     docs_url: str | None, support_email: str | None,
                                     community_url: str | None, developer: dict) -> dict:
    urgent_tickets = [t for t in open_tickets if t.get("priority") == "urgent"]
    return {
        "page_type": "app_support",
        "app": {"id": app["id"], "name": app["name"]},
        "developer": {"name": developer.get("display_name"), "response_time": developer.get("avg_response_hours", 24)},
        "tabs": [
            {"key": "faq", "title": f"FAQ ({len(faq)})", "icon": "❓"},
            {"key": "tickets", "title": f"Tickets ({len(open_tickets)})", "icon": "🎫",
             "urgent": len(urgent_tickets)},
            {"key": "docs", "title": "Documentation", "icon": "📚", "url": docs_url},
            {"key": "contact", "title": "Contact", "icon": "📧"},
            {"key": "community", "title": "Community", "icon": "💬", "url": community_url},
        ],
        "contact": {"email": support_email, "has_email": support_email is not None},
    }
