"""App Content Negotiation — manage response format negotiation.

Manages content negotiation:
- Register supported formats per endpoint
- Negotiate best format from Accept header
- Default format fallback
- Per-installation scoped configurations
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FormatConfig:
    """A supported response format."""

    media_type: str  # e.g., "application/json"
    quality: float = 1.0  # server preference 0-1
    charset: str = "utf-8"


@dataclass
class NegotiationResult:
    """Result of content negotiation."""

    media_type: str
    charset: str
    matched: bool  # True if matched Accept header, False if fallback


class AppContentNegotiation:
    """Manage response format negotiation."""

    def __init__(self) -> None:
        self._formats: dict[str, list[FormatConfig]] = {}
        self._defaults: dict[str, str] = {}

    def register_format(
        self, installation_id: str, media_type: str,
        quality: float = 1.0, charset: str = "utf-8",
    ) -> FormatConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not media_type:
            raise ValueError("media_type is required")
        if not (0 < quality <= 1):
            raise ValueError("quality must be between 0 and 1")

        fmt = FormatConfig(media_type=media_type, quality=quality, charset=charset)
        self._formats.setdefault(installation_id, []).append(fmt)

        # First registered format is default
        if installation_id not in self._defaults:
            self._defaults[installation_id] = media_type

        return fmt

    def set_default(self, installation_id: str, media_type: str) -> None:
        formats = self._formats.get(installation_id, [])
        if not any(f.media_type == media_type for f in formats):
            raise ValueError(f"Format {media_type} not registered")
        self._defaults[installation_id] = media_type

    def negotiate(self, installation_id: str, accept_header: str) -> NegotiationResult:
        """Negotiate best format from Accept header."""
        formats = self._formats.get(installation_id, [])
        if not formats:
            return NegotiationResult(
                media_type="application/json", charset="utf-8", matched=False,
            )

        # Parse accept header
        accepted = self._parse_accept(accept_header)

        # Find best match
        best: FormatConfig | None = None
        best_q = 0.0

        for fmt in formats:
            for accept_type, client_q in accepted:
                if self._type_matches(accept_type, fmt.media_type):
                    combined = client_q * fmt.quality
                    if combined > best_q:
                        best = fmt
                        best_q = combined

        if best:
            return NegotiationResult(
                media_type=best.media_type, charset=best.charset, matched=True,
            )

        # Fallback to default
        default_type = self._defaults.get(installation_id, formats[0].media_type)
        default_fmt = next((f for f in formats if f.media_type == default_type), formats[0])
        return NegotiationResult(
            media_type=default_fmt.media_type, charset=default_fmt.charset, matched=False,
        )

    def list_formats(self, installation_id: str) -> list[FormatConfig]:
        return list(self._formats.get(installation_id, []))

    def _parse_accept(self, header: str) -> list[tuple[str, float]]:
        if not header:
            return [("*/*", 1.0)]
        result = []
        for part in header.split(","):
            part = part.strip()
            q = 1.0
            if ";q=" in part:
                type_part, q_part = part.split(";q=", 1)
                part = type_part.strip()
                try:
                    q = float(q_part.strip())
                except ValueError:
                    q = 0.0
            result.append((part, q))
        return sorted(result, key=lambda x: x[1], reverse=True)

    def _type_matches(self, pattern: str, media_type: str) -> bool:
        if pattern == "*/*":
            return True
        if pattern == media_type:
            return True
        p_main = pattern.split("/")[0]
        m_main = media_type.split("/")[0]
        if pattern.endswith("/*") and p_main == m_main:
            return True
        return False
