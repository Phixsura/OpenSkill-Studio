"""Content Negotiator — HTTP Accept header parsing with quality-weighted selection.

Implements:
- Parse Accept header with quality factors (q=0.9)
- Media type matching with wildcards (*/*, application/*)
- Best match selection from available types
- Accept-Language negotiation
- Accept-Encoding negotiation
- 406 Not Acceptable detection
"""
from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass
class MediaRange:
    type: str      # e.g. "application"
    subtype: str   # e.g. "json"
    quality: float = 1.0
    params: dict = None

    def __post_init__(self):
        if self.params is None:
            self.params = {}

    @property
    def full_type(self) -> str:
        return f"{self.type}/{self.subtype}"

    def matches(self, content_type: str) -> bool:
        parts = content_type.split("/")
        if len(parts) != 2:
            return False
        ct, cs = parts
        if self.type == "*" and self.subtype == "*":
            return True
        if self.type == ct and self.subtype == "*":
            return True
        return self.type == ct and self.subtype == cs


class ContentNegotiatorService:
    def parse_accept(self, header: str) -> list[MediaRange]:
        """Parse Accept header into sorted list of MediaRanges."""
        if not header or header.strip() == "":
            return [MediaRange("*", "*", 1.0)]

        ranges = []
        for part in header.split(","):
            part = part.strip()
            if not part:
                continue
            segments = part.split(";")
            media = segments[0].strip()
            if "/" not in media:
                continue
            mtype, msubtype = media.split("/", 1)

            quality = 1.0
            params = {}
            for param in segments[1:]:
                param = param.strip()
                if "=" in param:
                    k, v = param.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k == "q":
                        try:
                            quality = float(v)
                        except ValueError:
                            quality = 0
                    else:
                        params[k] = v

            ranges.append(MediaRange(mtype.strip(), msubtype.strip(),
                                      quality, params))

        # Sort by quality (descending), then specificity
        ranges.sort(key=lambda r: (
            -r.quality,
            0 if r.type != "*" and r.subtype != "*" else
            1 if r.type != "*" else 2))
        return ranges

    def negotiate(self, accept_header: str,
                  available: list[str]) -> str | None:
        """Find best match from available content types.
        Returns None if no acceptable type (406)."""
        if not available:
            return None

        ranges = self.parse_accept(accept_header)
        best_match = None
        best_quality = -1

        for content_type in available:
            for media_range in ranges:
                if media_range.quality <= 0:
                    continue
                if media_range.matches(content_type):
                    # Prefer more specific matches
                    specificity = (0 if media_range.type != "*" else 1) + \
                                  (0 if media_range.subtype != "*" else 1)
                    score = media_range.quality - specificity * 0.001
                    if score > best_quality:
                        best_quality = score
                        best_match = content_type
                    break  # first match for this content type

        return best_match

    def negotiate_language(self, accept_language: str,
                           available: list[str]) -> str:
        """Negotiate Accept-Language. Returns best match or first available."""
        if not accept_language:
            return available[0] if available else "en"

        parsed = []
        for part in accept_language.split(","):
            part = part.strip()
            q = 1.0
            if ";q=" in part:
                lang, qval = part.split(";q=", 1)
                try:
                    q = float(qval.strip())
                except ValueError:
                    q = 0
                part = lang.strip()
            parsed.append((part, q))

        parsed.sort(key=lambda x: -x[1])

        for lang, q in parsed:
            if q <= 0:
                continue
            for avail in available:
                if avail == lang or avail.startswith(lang + "-") or lang == "*":
                    return avail

        return available[0] if available else "en"

    def negotiate_encoding(self, accept_encoding: str,
                           available: list[str]) -> str:
        """Negotiate Accept-Encoding."""
        if not accept_encoding:
            return "identity"
        return self.negotiate_language(accept_encoding, available) or "identity"
