"""API Consumer API Version Pinning — pin consumers to specific API versions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class VersionPin:
    consumer_id: str
    pinned_version: str
    pinned_at: float = field(default_factory=time.time)
    reason: str = ""
    auto_upgrade: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiVersionPinning:
    def __init__(self) -> None:
        self._pins: dict[tuple[str, str], VersionPin] = {}

    def pin(self, installation_id: str, consumer_id: str, version: str, reason: str = "", auto_upgrade: bool = False) -> VersionPin:
        if not installation_id: raise ValueError("installation_id is required")
        if not version: raise ValueError("version is required")
        pin = VersionPin(consumer_id=consumer_id, pinned_version=version, reason=reason, auto_upgrade=auto_upgrade)
        self._pins[(installation_id, consumer_id)] = pin
        return pin

    def unpin(self, installation_id: str, consumer_id: str) -> bool:
        key = (installation_id, consumer_id)
        if key in self._pins: del self._pins[key]; return True
        return False

    def get_version(self, installation_id: str, consumer_id: str, default: str = "latest") -> str:
        pin = self._pins.get((installation_id, consumer_id))
        return pin.pinned_version if pin else default

    def pinned_consumers(self, installation_id: str, version: str | None = None) -> list[VersionPin]:
        pins = [p for (inst, _), p in self._pins.items() if inst == installation_id]
        if version: pins = [p for p in pins if p.pinned_version == version]
        return pins

    def auto_upgrade_consumers(self, installation_id: str) -> list[VersionPin]:
        return [p for (inst, _), p in self._pins.items() if inst == installation_id and p.auto_upgrade]

    def list_pins(self, installation_id: str) -> list[VersionPin]:
        return [p for (inst, _), p in self._pins.items() if inst == installation_id]
