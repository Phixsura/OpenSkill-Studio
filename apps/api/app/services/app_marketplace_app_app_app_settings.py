"""App settings — app configuration settings page builder."""

import html

SECTIONS = {
    "general": {"label": "General", "icon": "⚙️", "fields": [
        {"key": "name", "label": "App Name", "type": "text", "required": True},
        {"key": "description", "label": "Description", "type": "textarea"},
        {"key": "icon", "label": "Icon", "type": "emoji"},
        {"key": "category", "label": "Category", "type": "select", "options": ["tools", "productivity", "communication"]},
    ]},
    "visibility": {"label": "Visibility", "icon": "👁️", "fields": [
        {"key": "published", "label": "Published", "type": "toggle"},
        {"key": "listed", "label": "Listed in Marketplace", "type": "toggle"},
        {"key": "searchable", "label": "Searchable", "type": "toggle"},
    ]},
    "danger": {"label": "Danger Zone", "icon": "⚠️", "fields": [
        {"key": "transfer", "label": "Transfer Ownership", "type": "action"},
        {"key": "archive", "label": "Archive App", "type": "action"},
        {"key": "delete", "label": "Delete App", "type": "action_danger"},
    ]},
}


def build_settings_page(*, app: dict) -> dict:
    sections = []
    for sid, sec in SECTIONS.items():
        fields = []
        for f in sec["fields"]:
            fields.append({**f, "label": html.escape(f["label"]),
                           "value": app.get(f["key"])})
        sections.append({"id": sid, "label": sec["label"], "icon": sec["icon"],
                          "fields": fields, "field_count": len(fields)})
    return {"sections": sections, "section_count": len(sections),
            "app_name": html.escape(app.get("name", ""))}
