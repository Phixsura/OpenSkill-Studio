"""Terms page — terms of service and legal pages."""

LEGAL_PAGES = {
    "terms": {"title": "Terms of Service", "last_updated": "2026-10-01",
              "sections": ["Introduction", "Account Terms", "API Usage", "Marketplace Rules",
                            "App Developer Agreement", "Intellectual Property", "Limitation of Liability",
                            "Termination", "Changes to Terms", "Contact"]},
    "privacy": {"title": "Privacy Policy", "last_updated": "2026-10-01",
                 "sections": ["Data Collection", "Data Use", "Data Sharing", "Data Retention",
                               "Your Rights", "Cookies", "Security", "Children", "Changes", "Contact"]},
    "acceptable_use": {"title": "Acceptable Use Policy", "last_updated": "2026-09-15",
                         "sections": ["Permitted Use", "Prohibited Use", "Content Standards",
                                       "Enforcement", "Reporting"]},
    "developer_agreement": {"title": "Developer Agreement", "last_updated": "2026-10-01",
                              "sections": ["Eligibility", "App Requirements", "Review Process",
                                            "Revenue Sharing", "Support Obligations", "Termination"]},
}


def build_legal_page(*, page_id: str) -> dict | None:
    page = LEGAL_PAGES.get(page_id)
    if not page:
        return None
    return {"page_type": "legal", "id": page_id, **page,
            "section_count": len(page["sections"])}


def get_legal_pages_index() -> list[dict]:
    return [{"id": k, "title": v["title"], "last_updated": v["last_updated"]}
            for k, v in LEGAL_PAGES.items()]
