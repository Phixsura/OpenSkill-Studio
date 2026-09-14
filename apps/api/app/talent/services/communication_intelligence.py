"""Communication intelligence — email templates, digests, message templates, bulk messaging.

Closes gaps: #146-#155 (communication).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

# ---------------------------------------------------------------------------
# Gap #146: Email notification templates
# ---------------------------------------------------------------------------

EMAIL_TEMPLATES: dict[str, dict] = {
    "application_status_changed": {
        "subject": "Your application status has been updated",
        "body_template": "Hi {candidate_name},\n\nYour application for {role_title} has moved to: {new_status}.\n\nView details: {app_url}\n\n— OpenSkill Studio",
    },
    "new_match_found": {
        "subject": "New opportunity matches your profile",
        "body_template": "Hi {candidate_name},\n\nWe found a new opportunity that matches your skills:\n\n{opportunity_title} at {employer_name}\nMatch: {match_score}%\n\nView: {opportunity_url}\n\n— OpenSkill Studio",
    },
    "credential_issued": {
        "subject": "Congratulations! You earned a new credential",
        "body_template": "Hi {candidate_name},\n\nYou have been awarded: {credential_type}\n\nView and share: {credential_url}\n\n— OpenSkill Studio",
    },
    "interview_scheduled": {
        "subject": "Interview scheduled: {role_title}",
        "body_template": "Hi {candidate_name},\n\nYour interview for {role_title} has been scheduled.\n\nDate: {interview_date}\nTime: {interview_time}\nFormat: {interview_format}\n\n{meeting_url}\n\n— OpenSkill Studio",
    },
    "offer_extended": {
        "subject": "You have received an offer!",
        "body_template": "Hi {candidate_name},\n\nCongratulations! You have received an offer for {role_title}.\n\nPlease review and respond before {deadline}.\n\nView: {offer_url}\n\n— OpenSkill Studio",
    },
    "endorsement_received": {
        "subject": "Someone endorsed your skill",
        "body_template": "Hi {candidate_name},\n\n{endorser_name} endorsed your {capability_name} skill.\n\nView: {profile_url}\n\n— OpenSkill Studio",
    },
    "evidence_expiring": {
        "subject": "Evidence expiring soon",
        "body_template": "Hi {candidate_name},\n\nYour evidence for {capability_name} expires in {days_remaining} days.\n\nConsider renewing or adding new evidence.\n\n— OpenSkill Studio",
    },
    "offer_deadline_reminder": {
        "subject": "Offer deadline approaching: {role_title}",
        "body_template": "Hi {candidate_name},\n\nYour offer for {role_title} expires in {hours_remaining} hours.\n\nPlease respond before the deadline.\n\nView: {offer_url}\n\n— OpenSkill Studio",
    },
}


def render_email_template(template_key: str, context: dict) -> dict | None:
    """Render an email template with context variables."""
    template = EMAIL_TEMPLATES.get(template_key)
    if not template:
        return None
    try:
        subject = template["subject"].format(**context)
        body = template["body_template"].format(**context)
    except KeyError:
        subject = template["subject"]
        body = template["body_template"]
    return {"subject": subject, "body": body, "template_key": template_key}


def list_email_templates() -> list[str]:
    return sorted(EMAIL_TEMPLATES.keys())


# ---------------------------------------------------------------------------
# Gap #149: Notification digest
# ---------------------------------------------------------------------------

DIGEST_FREQUENCIES = frozenset({"daily", "weekly", "none"})


@dataclass(frozen=True, slots=True)
class DigestPreference:
    user_id: str
    frequency: str
    last_sent_at: datetime | None


def build_digest(notifications: list[dict], frequency: str) -> dict:
    """Build a notification digest from unread notifications."""
    if not notifications:
        return {"count": 0, "sections": [], "frequency": frequency}

    by_type: dict[str, list] = {}
    for n in notifications:
        t = n.get("event_type", "other")
        by_type.setdefault(t, []).append(n)

    sections = [
        {"event_type": t, "count": len(items), "latest": items[0].get("title", "")}
        for t, items in sorted(by_type.items())
    ]

    return {
        "count": len(notifications),
        "sections": sections,
        "frequency": frequency,
        "generated_at": datetime.now(UTC).isoformat(),
    }


# ---------------------------------------------------------------------------
# Gap #152: Message templates
# ---------------------------------------------------------------------------

MESSAGE_TEMPLATES: dict[str, dict] = {
    "thank_you": {
        "label": "Thank you",
        "content": "Thank you for your application. We will review it and get back to you shortly.",
    },
    "next_steps": {
        "label": "Next steps",
        "content": "Thank you for your interest. The next step is a {stage_type} interview. We will send scheduling details soon.",
    },
    "request_info": {
        "label": "Request information",
        "content": "Could you please provide additional information about {topic}? This will help us process your application.",
    },
    "rejection_kind": {
        "label": "Rejection (kind)",
        "content": "After careful consideration, we have decided to move forward with other candidates. We appreciate your interest and encourage you to apply for future opportunities.",
    },
    "schedule_interview": {
        "label": "Schedule interview",
        "content": "We would like to schedule a {stage_type} interview with you. Please select a time that works for you using the link below.",
    },
}


def get_message_template(key: str) -> dict | None:
    return MESSAGE_TEMPLATES.get(key)


def list_message_templates() -> list[str]:
    return sorted(MESSAGE_TEMPLATES.keys())


def render_message_template(key: str, context: dict) -> str | None:
    """Render a message template with context."""
    template = MESSAGE_TEMPLATES.get(key)
    if not template:
        return None
    try:
        return template["content"].format(**context)
    except KeyError:
        return template["content"]


# ---------------------------------------------------------------------------
# Gap #153: Bulk messaging
# ---------------------------------------------------------------------------

MAX_BULK_RECIPIENTS = 100


def validate_bulk_message(
    recipient_ids: list[str],
    content: str,
) -> list[str]:
    """Validate a bulk message request."""
    errors = []
    if not recipient_ids:
        errors.append("At least one recipient required")
    if len(recipient_ids) > MAX_BULK_RECIPIENTS:
        errors.append(f"Maximum {MAX_BULK_RECIPIENTS} recipients per bulk message")
    if len(set(recipient_ids)) != len(recipient_ids):
        errors.append("Duplicate recipients not allowed")
    if not content or len(content) < 5:
        errors.append("Message content must be at least 5 characters")
    if len(content) > 5000:
        errors.append("Message content must be under 5000 characters")
    return errors
