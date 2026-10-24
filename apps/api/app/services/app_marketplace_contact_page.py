"""Contact page — contact form and support channels."""


def build_contact_page(*, channels: list[dict] | None = None) -> dict:
    default_channels = [
        {"id": "email", "label": "Email Support", "icon": "📧", "value": "support@openskill.dev",
         "description": "Get a response within 24 hours", "url": "mailto:support@openskill.dev"},
        {"id": "community", "label": "Community Forum", "icon": "💬", "value": "community.openskill.dev",
         "description": "Ask questions, share ideas", "url": "/community"},
        {"id": "docs", "label": "Documentation", "icon": "📚", "value": "docs.openskill.dev",
         "description": "Guides, tutorials, and API reference", "url": "/docs"},
        {"id": "status", "label": "System Status", "icon": "📊", "value": "status.openskill.dev",
         "description": "Real-time platform status", "url": "/status"},
    ]
    return {
        "page_type": "contact",
        "channels": channels or default_channels,
        "form": {
            "fields": [
                {"name": "name", "label": "Name", "type": "text", "required": True},
                {"name": "email", "label": "Email", "type": "email", "required": True},
                {"name": "subject", "label": "Subject", "type": "select",
                 "options": ["General", "Bug Report", "Feature Request", "Billing", "Partnership"]},
                {"name": "message", "label": "Message", "type": "textarea", "required": True},
            ],
        },
        "office": {"address": "San Francisco, CA", "hours": "Mon-Fri 9am-6pm PT"},
    }


def submit_contact_form(*, name: str, email: str, subject: str, message: str) -> dict:
    if not name or not email or not message:
        return {"success": False, "error": "All required fields must be filled"}
    if "@" not in email:
        return {"success": False, "error": "Invalid email address"}
    return {"success": True, "message": "Thanks! We'll get back to you within 24 hours.",
            "ticket_id": f"TICKET-{hash(email) % 10000:04d}"}
