"""Slack notification builder — construct Block Kit messages for alerts."""
from __future__ import annotations
import html


def build_alert_message(*, title: str, severity: str, message: str,
                          service: str = "", link: str = "") -> dict:
    color = {"critical": "#DC2626", "warning": "#F59E0B", "info": "#3B82F6"}.get(severity, "#6B7280")
    emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(severity, "📌")
    safe_title = html.escape(title)
    safe_msg = html.escape(message)
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} {safe_title}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": safe_msg}},
    ]
    if service:
        blocks.append({"type": "context", "elements": [
            {"type": "mrkdwn", "text": f"Service: *{html.escape(service)}*"}]})
    if link:
        blocks.append({"type": "actions", "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "View Details"},
             "url": link, "style": "primary"}]})
    return {"blocks": blocks, "color": color, "text": f"{emoji} {safe_title}: {safe_msg}"}


def build_deploy_message(*, app: str, version: str, deployer: str,
                           status: str = "success") -> dict:
    emoji = "✅" if status == "success" else "❌"
    color = "#10B981" if status == "success" else "#EF4444"
    return {
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn",
             "text": f"{emoji} *{html.escape(app)}* deployed *{html.escape(version)}* by {html.escape(deployer)}"}},
        ],
        "color": color, "text": f"{emoji} Deploy {status}: {app} {version}",
    }
