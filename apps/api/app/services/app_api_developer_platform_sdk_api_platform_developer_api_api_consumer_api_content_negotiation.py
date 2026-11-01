"""API Consumer Content Negotiation — manage response format preferences."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ContentPreference:
    consumer_id: str
    preferred_format: str = "json"  # "json", "xml", "msgpack", "protobuf"
    accepted_formats: list[str] = field(default_factory=lambda: ["json"])
    preferred_encoding: str = "utf-8"
    compression: str = "none"  # "none", "gzip", "br"

VALID_FORMATS = {"json", "xml", "msgpack", "protobuf", "csv", "yaml"}
VALID_COMPRESSIONS = {"none", "gzip", "br", "zstd"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiContentNegotiation:
    def __init__(self) -> None:
        self._prefs: dict[tuple[str, str], ContentPreference] = {}

    def set_preference(self, installation_id: str, pref: ContentPreference) -> ContentPreference:
        if not installation_id: raise ValueError("installation_id is required")
        if pref.preferred_format not in VALID_FORMATS: raise ValueError(f"Invalid format: {pref.preferred_format}")
        invalid = set(pref.accepted_formats) - VALID_FORMATS
        if invalid: raise ValueError(f"Invalid formats: {invalid}")
        if pref.compression not in VALID_COMPRESSIONS: raise ValueError(f"Invalid compression: {pref.compression}")
        if pref.preferred_format not in pref.accepted_formats:
            pref.accepted_formats.append(pref.preferred_format)
        self._prefs[(installation_id, pref.consumer_id)] = pref
        return pref

    def negotiate(self, installation_id: str, consumer_id: str, server_formats: list[str]) -> str:
        pref = self._prefs.get((installation_id, consumer_id))
        if pref is None: return "json"
        if pref.preferred_format in server_formats: return pref.preferred_format
        for fmt in pref.accepted_formats:
            if fmt in server_formats: return fmt
        return server_formats[0] if server_formats else "json"

    def get_preference(self, installation_id: str, consumer_id: str) -> ContentPreference | None:
        return self._prefs.get((installation_id, consumer_id))

    def list_preferences(self, installation_id: str) -> list[ContentPreference]:
        return [p for (inst, _), p in self._prefs.items() if inst == installation_id]
