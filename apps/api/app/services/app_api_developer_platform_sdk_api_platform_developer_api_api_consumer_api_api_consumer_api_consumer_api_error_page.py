"""Consumer API Error Page — customize error responses per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorTemplate:
    status_code: int
    error_code: str
    title: str
    message_template: str  # supports {{detail}} placeholder
    docs_url: str = ""
    support_email: str = ""

@dataclass
class ErrorResponse:
    status_code: int
    error_code: str
    title: str
    message: str
    docs_url: str
    support_email: str

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiErrorPage:
    def __init__(self) -> None:
        self._templates: dict[tuple[str, int], ErrorTemplate] = {}  # (inst, status)
        self._consumer_overrides: dict[tuple[str, str, int], ErrorTemplate] = {}  # (inst, consumer, status)

    def set_default(self, installation_id: str, template: ErrorTemplate) -> ErrorTemplate:
        if not installation_id:
            raise ValueError("installation_id is required")
        if template.status_code < 400 or template.status_code > 599:
            raise ValueError("status_code must be 4xx or 5xx")
        self._templates[(installation_id, template.status_code)] = template
        return template

    def set_consumer_override(self, installation_id: str, consumer_id: str, template: ErrorTemplate) -> ErrorTemplate:
        if template.status_code < 400 or template.status_code > 599:
            raise ValueError("status_code must be 4xx or 5xx")
        self._consumer_overrides[(installation_id, consumer_id, template.status_code)] = template
        return template

    def render(self, installation_id: str, consumer_id: str, status_code: int, detail: str = "") -> ErrorResponse:
        # Consumer override first, then default, then fallback
        template = self._consumer_overrides.get((installation_id, consumer_id, status_code))
        if not template:
            template = self._templates.get((installation_id, status_code))
        if not template:
            template = ErrorTemplate(status_code=status_code, error_code=f"ERR_{status_code}", title=f"Error {status_code}", message_template="{{detail}}")
        message = template.message_template.replace("{{detail}}", detail)
        return ErrorResponse(status_code=template.status_code, error_code=template.error_code, title=template.title, message=message, docs_url=template.docs_url, support_email=template.support_email)

    def list_templates(self, installation_id: str) -> list[ErrorTemplate]:
        return [t for (inst, _), t in self._templates.items() if inst == installation_id]
