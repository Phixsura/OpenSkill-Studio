"""API docs page — interactive API documentation page builder."""

import html

DOC_SECTIONS = [
    {"id": "auth", "title": "Authentication", "icon": "🔑",
     "endpoints": [{"method": "POST", "path": "/api/v1/auth/token", "summary": "Get access token"}]},
    {"id": "apps", "title": "Apps", "icon": "📦",
     "endpoints": [
         {"method": "GET", "path": "/api/v1/apps", "summary": "List apps"},
         {"method": "POST", "path": "/api/v1/apps", "summary": "Create app"},
         {"method": "GET", "path": "/api/v1/apps/{id}", "summary": "Get app"},
         {"method": "PUT", "path": "/api/v1/apps/{id}", "summary": "Update app"},
         {"method": "DELETE", "path": "/api/v1/apps/{id}", "summary": "Delete app"},
     ]},
    {"id": "webhooks", "title": "Webhooks", "icon": "🔗",
     "endpoints": [
         {"method": "GET", "path": "/api/v1/webhooks", "summary": "List webhooks"},
         {"method": "POST", "path": "/api/v1/webhooks", "summary": "Create webhook"},
     ]},
]


def build_docs_page(*, base_url: str = "https://api.openskill.dev") -> dict:
    sections = []
    total_endpoints = 0
    for sec in DOC_SECTIONS:
        eps = [{"method": e["method"], "path": e["path"],
                "full_url": f"{base_url}{e['path']}",
                "summary": html.escape(e["summary"])} for e in sec["endpoints"]]
        total_endpoints += len(eps)
        sections.append({"id": sec["id"], "title": sec["title"],
                          "icon": sec["icon"], "endpoints": eps,
                          "endpoint_count": len(eps)})
    return {"sections": sections, "total_endpoints": total_endpoints,
            "base_url": base_url, "version": "v1"}
