"""Email template — transactional email builder."""

import html

TEMPLATES = {
    "welcome": {"subject": "Welcome to {app_name}!", "preheader": "Get started in minutes"},
    "invite": {"subject": "You've been invited to {app_name}", "preheader": "Join the team"},
    "reset_password": {"subject": "Reset your {app_name} password", "preheader": "Password reset requested"},
    "billing": {"subject": "{app_name} — Invoice #{invoice_id}", "preheader": "Your invoice is ready"},
    "notification": {"subject": "[{app_name}] {title}", "preheader": "{preview}"},
}


def build_email(*, template_id: str, variables: dict[str, str],
                  body_html: str = "") -> dict:
    tmpl = TEMPLATES.get(template_id)
    if not tmpl:
        return {"error": f"Unknown template: {template_id}"}
    safe = {k: html.escape(v) for k, v in variables.items()}
    try:
        subject = tmpl["subject"].format(**safe)
        preheader = tmpl["preheader"].format(**safe)
    except KeyError as e:
        return {"error": f"Missing variable: {e}"}
    return {"template_id": template_id, "subject": subject, "preheader": preheader,
            "body_html": html.escape(body_html) if body_html else "", "variables": safe,
            "text_preview": f"{subject} — {preheader}"}


def list_templates() -> list[dict]:
    return [{"id": k, "subject_template": v["subject"],
             "preheader": v["preheader"]} for k, v in TEMPLATES.items()]
