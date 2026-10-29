"""App API Developer Platform Release Readiness — pre-release quality gate check."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ReleaseCheck:
    name: str
    passed: bool = False
    required: bool = True
    details: str = ""

@dataclass
class ReleaseReadiness:
    version: str
    checks: list[ReleaseCheck] = field(default_factory=list)

    @property
    def passed_count(self) -> int: return sum(1 for c in self.checks if c.passed)
    @property
    def total_count(self) -> int: return len(self.checks)
    @property
    def all_required_passed(self) -> bool: return all(c.passed for c in self.checks if c.required)
    @property
    def readiness_pct(self) -> float: return round(self.passed_count / self.total_count * 100, 1) if self.total_count > 0 else 0.0
    @property
    def verdict(self) -> str:
        if self.all_required_passed and self.readiness_pct == 100: return "SHIP_IT"
        if self.all_required_passed: return "SHIP_WITH_CAVEATS"
        return "HOLD"

class AppAPIDeveloperPlatformSDKApiPlatformReleaseReadiness:
    def __init__(self) -> None:
        self._readiness: dict[tuple[str, str], ReleaseReadiness] = {}

    def create(self, installation_id: str, version: str, checks: list[dict]) -> ReleaseReadiness:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, version)
        parsed = [ReleaseCheck(name=c["name"], passed=c.get("passed", False), required=c.get("required", True), details=c.get("details", "")) for c in checks]
        r = ReleaseReadiness(version=version, checks=parsed)
        self._readiness[key] = r
        return r

    def get(self, installation_id: str, version: str) -> ReleaseReadiness | None:
        return self._readiness.get((installation_id, version))

    def all_releases(self, installation_id: str) -> list[ReleaseReadiness]:
        return [r for (inst, _), r in self._readiness.items() if inst == installation_id]
