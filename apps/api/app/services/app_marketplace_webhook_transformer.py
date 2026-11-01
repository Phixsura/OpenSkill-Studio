"""Webhook Transformer — transform webhook payloads between formats.

Maps incoming webhook payloads to the OpenSkill event format and
outgoing events to third-party webhook formats (Slack, Discord, etc).
"""
from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class TransformRule:
    name: str
    source_field: str
    target_field: str
    transform: str = "copy"  # copy, rename, template, default, omit


class WebhookTransformer:
    """Transforms webhook payloads between formats."""

    def __init__(self):
        self._templates: dict[str, list[TransformRule]] = {}

    def register_template(self, template_name: str, rules: list[TransformRule]) -> None:
        self._templates[template_name] = rules

    def transform(self, payload: dict, template_name: str,
                  defaults: dict | None = None) -> dict:
        """Apply a transform template to a payload."""
        rules = self._templates.get(template_name, [])
        if not rules:
            return deepcopy(payload)  # pass-through

        result = {}
        defaults = defaults or {}

        for rule in rules:
            if rule.transform == "omit":
                continue
            elif rule.transform == "copy":
                value = self._get_nested(payload, rule.source_field)
                if value is not None:
                    self._set_nested(result, rule.target_field, value)
            elif rule.transform == "default":
                value = self._get_nested(payload, rule.source_field)
                self._set_nested(result, rule.target_field,
                                 value if value is not None else defaults.get(rule.source_field, ""))
            elif rule.transform == "template":
                # source_field is a template string like "{event_type}: {message}"
                formatted = rule.source_field
                for key, val in payload.items():
                    if isinstance(val, str):
                        formatted = formatted.replace(f"{{{key}}}", val)
                self._set_nested(result, rule.target_field, formatted)

        return result

    def to_slack(self, event_type: str, payload: dict) -> dict:
        """Transform to Slack incoming webhook format."""
        text = f"*{event_type}*"
        if "message" in payload:
            text += f"\n{payload['message']}"
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
        if "url" in payload:
            blocks.append({"type": "actions", "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "View"},
                 "url": payload["url"]}]})
        return {"text": text, "blocks": blocks}

    def to_discord(self, event_type: str, payload: dict) -> dict:
        """Transform to Discord webhook format."""
        embed = {
            "title": event_type.replace(".", " ").title(),
            "description": payload.get("message", ""),
            "color": 5814783,  # blue
        }
        fields = [{"name": k, "value": str(v), "inline": True}
                  for k, v in payload.items() if k not in ("message", "url")]
        if fields:
            embed["fields"] = fields[:10]
        return {"embeds": [embed]}

    def _get_nested(self, data: dict, path: str) -> object | None:
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    def _set_nested(self, data: dict, path: str, value: object) -> None:
        parts = path.split(".")
        current = data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value
