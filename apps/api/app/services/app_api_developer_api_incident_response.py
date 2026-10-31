"""App API Developer API Incident Response — manage incident response playbooks."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import structlog

log = structlog.get_logger()

class ResponseStatus(str, Enum):
    IDLE = "idle"
    ACTIVATED = "activated"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"

@dataclass
class IncidentResponse:
    response_id: str
    incident_type: str
    playbook_steps: list[str]
    status: ResponseStatus = ResponseStatus.IDLE
    current_step: int = 0
    responders: list[str] = field(default_factory=list)

class AppAPIDeveloperAPIIncidentResponse:
    def __init__(self) -> None:
        self._responses: dict[tuple[str, str], IncidentResponse] = {}

    def create(self, installation_id: str, response_id: str, incident_type: str, playbook_steps: list[str], responders: list[str] | None = None) -> IncidentResponse:
        if not installation_id: raise ValueError("installation_id is required")
        if not playbook_steps: raise ValueError("at least one step required")
        key = (installation_id, response_id)
        if key in self._responses: raise ValueError(f"Response {response_id} exists")
        r = IncidentResponse(response_id=response_id, incident_type=incident_type, playbook_steps=playbook_steps, responders=responders or [])
        self._responses[key] = r
        return r

    def activate(self, installation_id: str, response_id: str) -> IncidentResponse:
        r = self._get(installation_id, response_id)
        r.status = ResponseStatus.ACTIVATED
        return r

    def advance_step(self, installation_id: str, response_id: str) -> IncidentResponse:
        r = self._get(installation_id, response_id)
        if r.current_step < len(r.playbook_steps) - 1:
            r.current_step += 1
            r.status = ResponseStatus.MITIGATING
        else:
            r.status = ResponseStatus.RESOLVED
        return r

    def active_responses(self, installation_id: str) -> list[IncidentResponse]:
        return [r for (inst, _), r in self._responses.items() if inst == installation_id and r.status in (ResponseStatus.ACTIVATED, ResponseStatus.MITIGATING)]

    def list_responses(self, installation_id: str) -> list[IncidentResponse]:
        return [r for (inst, _), r in self._responses.items() if inst == installation_id]

    def _get(self, installation_id: str, response_id: str) -> IncidentResponse:
        r = self._responses.get((installation_id, response_id))
        if r is None: raise KeyError(f"Response {response_id} not found")
        return r
