"""Copy generator — marketing copy templates for app listings."""

import html

TEMPLATES = {
    "hero": "{name} — {tagline}. {benefit}.",
    "cta": "Get started with {name} today. {action}.",
    "feature": "✨ {feature_name}: {feature_desc}",
    "social": "🚀 Check out {name}! {tagline} #openskill #marketplace",
}


def generate_copy(*, template_id: str, variables: dict[str, str]) -> dict:
    template = TEMPLATES.get(template_id)
    if not template:
        return {"error": f"Unknown template: {template_id}"}
    safe_vars = {k: html.escape(v) for k, v in variables.items()}
    try:
        text = template.format(**safe_vars)
    except KeyError as e:
        return {"error": f"Missing variable: {e}"}
    return {"text": text, "template_id": template_id, "char_count": len(text),
            "variables_used": list(safe_vars.keys())}


def build_copy_set(*, app_name: str, tagline: str, benefit: str) -> dict:
    copies = {}
    for tid in TEMPLATES:
        r = generate_copy(template_id=tid, variables={
            "name": app_name, "tagline": tagline, "benefit": benefit,
            "action": "Sign up free", "feature_name": "Core",
            "feature_desc": tagline,
        })
        if "text" in r:
            copies[tid] = r["text"]
    return {"copies": copies, "count": len(copies), "app_name": html.escape(app_name)}
