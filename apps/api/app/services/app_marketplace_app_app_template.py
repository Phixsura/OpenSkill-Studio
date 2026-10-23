"""App template — starter templates for building marketplace apps."""

import secrets


TEMPLATES = [
    {"id": "basic", "name": "Basic App", "icon": "📦", "description": "Minimal app scaffold",
     "tech": ["TypeScript"], "files": 5, "category": "starter"},
    {"id": "react-widget", "name": "React Widget", "icon": "⚛️", "description": "Embeddable React component",
     "tech": ["React", "TypeScript"], "files": 12, "category": "frontend"},
    {"id": "api-integration", "name": "API Integration", "icon": "🔌", "description": "REST API connector",
     "tech": ["TypeScript", "Node.js"], "files": 8, "category": "backend"},
    {"id": "webhook-handler", "name": "Webhook Handler", "icon": "🪝", "description": "Process incoming webhooks",
     "tech": ["TypeScript"], "files": 6, "category": "backend"},
    {"id": "fullstack", "name": "Full-Stack App", "icon": "🏗️", "description": "Complete frontend + backend",
     "tech": ["React", "Node.js", "TypeScript"], "files": 25, "category": "fullstack"},
    {"id": "data-pipeline", "name": "Data Pipeline", "icon": "🔄", "description": "ETL data processor",
     "tech": ["Python"], "files": 10, "category": "backend"},
]


def list_templates(*, category: str | None = None) -> dict:
    filtered = TEMPLATES if not category else [t for t in TEMPLATES if t["category"] == category]
    categories = sorted(set(t["category"] for t in TEMPLATES))
    return {"templates": filtered, "total": len(filtered), "categories": categories}


def scaffold_from_template(*, template_id: str, app_name: str) -> dict:
    template = next((t for t in TEMPLATES if t["id"] == template_id), None)
    if not template:
        return {"error": f"Template not found: {template_id}"}
    project_id = f"proj_{secrets.token_urlsafe(8)}"
    return {
        "project_id": project_id,
        "app_name": app_name,
        "template": template["name"],
        "files_created": template["files"],
        "tech_stack": template["tech"],
        "next_steps": ["Install dependencies", "Configure API keys", "Start development server"],
    }
