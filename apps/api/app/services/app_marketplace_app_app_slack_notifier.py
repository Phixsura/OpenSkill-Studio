"""Slack notifier — Slack webhook message builder."""

import html
import json
from urllib.parse import urlparse


def build_slack_message(*, text: str, channel: str | None = None,
                         blocks: list[dict] | None = None,
                         color: str = "#3B82F6") -> dict:
    payload: dict = {"text": text}
    if channel:
        payload["channel"] = channel
    if blocks:
        payload["attachments"] = [{"color": color, "blocks": blocks}]
    return {"payload": json.dumps(payload), "text": text, "has_blocks": blocks is not None}


def build_app_event_message(*, app_name: str, event: str, actor: str,
                              details: str = "") -> dict:
    icons = {"installed": "📦", "updated": "🔄", "published": "🚀",
             "reviewed": "⭐", "deleted": "🗑️"}
    icon = icons.get(event, "📌")
    text = f"{icon} *{html.escape(app_name)}* was {event} by {html.escape(actor)}"
    if details:
        text += f"\n> {html.escape(details)}"
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
    return build_slack_message(text=text, blocks=blocks)
