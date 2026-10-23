"""Landing page builder — create custom landing pages for apps."""


def build_app_landing_page(*, app: dict, sections: list[dict], theme: str = "default") -> dict:
    page_sections = []
    for s in sections:
        page_sections.append({
            "type": s.get("type", "text"),
            "content": s.get("content", {}),
            "order": s.get("order", 0),
        })
    page_sections.sort(key=lambda x: x["order"])
    return {
        "page_type": "app_landing",
        "app": {"name": app["name"], "slug": app.get("slug")},
        "theme": theme,
        "sections": page_sections,
        "section_count": len(page_sections),
        "seo": {"title": f"{app['name']} — Built on OpenSkill"},
    }


SECTION_TEMPLATES = {
    "hero": {"type": "hero", "fields": ["title", "subtitle", "cta_label", "cta_url", "image"]},
    "features": {"type": "features", "fields": ["title", "items"]},
    "testimonials": {"type": "testimonials", "fields": ["title", "quotes"]},
    "pricing": {"type": "pricing", "fields": ["plans"]},
    "faq": {"type": "faq", "fields": ["title", "items"]},
    "cta": {"type": "cta", "fields": ["title", "subtitle", "button_label", "button_url"]},
}


def get_section_templates() -> dict:
    return SECTION_TEMPLATES
