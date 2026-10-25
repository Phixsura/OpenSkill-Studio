"""CSP Policy — Content Security Policy management for extension UIs.

Generates and validates Content Security Policy headers for extension
iframes, ensuring they can only load approved resources.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CSPDirectives:
    default_src: list[str] = field(default_factory=lambda: ["'self'"])
    script_src: list[str] = field(default_factory=lambda: ["'self'"])
    style_src: list[str] = field(default_factory=lambda: ["'self'", "'unsafe-inline'"])
    img_src: list[str] = field(default_factory=lambda: ["'self'", "data:", "https:"])
    connect_src: list[str] = field(default_factory=lambda: ["'self'"])
    frame_src: list[str] = field(default_factory=lambda: ["'none'"])
    font_src: list[str] = field(default_factory=lambda: ["'self'"])
    object_src: list[str] = field(default_factory=lambda: ["'none'"])
    base_uri: list[str] = field(default_factory=lambda: ["'self'"])


class CSPPolicyManager:
    """Manages Content Security Policies for extension sandboxes."""

    def __init__(self):
        self._policies: dict[str, CSPDirectives] = {}
        self._global_blocklist: set[str] = set()

    def set_policy(self, extension_id: str, directives: CSPDirectives) -> None:
        self._policies[extension_id] = directives

    def get_policy(self, extension_id: str) -> CSPDirectives:
        return self._policies.get(extension_id, CSPDirectives())

    def add_allowed_source(self, extension_id: str, directive: str, source: str) -> bool:
        """Add an allowed source to a specific directive."""
        policy = self._policies.setdefault(extension_id, CSPDirectives())
        sources = getattr(policy, directive, None)
        if sources is None:
            return False
        if source in self._global_blocklist:
            return False
        if source not in sources:
            sources.append(source)
        return True

    def remove_allowed_source(self, extension_id: str, directive: str, source: str) -> bool:
        policy = self._policies.get(extension_id)
        if not policy:
            return False
        sources = getattr(policy, directive, None)
        if sources and source in sources:
            sources.remove(source)
            return True
        return False

    def add_to_blocklist(self, domain: str) -> None:
        self._global_blocklist.add(domain)

    def generate_header(self, extension_id: str) -> str:
        """Generate a CSP header string."""
        policy = self.get_policy(extension_id)
        parts = []
        for directive_name, attr_name in [
            ("default-src", "default_src"), ("script-src", "script_src"),
            ("style-src", "style_src"), ("img-src", "img_src"),
            ("connect-src", "connect_src"), ("frame-src", "frame_src"),
            ("font-src", "font_src"), ("object-src", "object_src"),
            ("base-uri", "base_uri"),
        ]:
            sources = getattr(policy, attr_name, [])
            if sources:
                parts.append(f"{directive_name} {' '.join(sources)}")
        return "; ".join(parts)

    def validate_source(self, extension_id: str, directive: str, source: str) -> bool:
        """Check if a source is allowed by the policy."""
        policy = self.get_policy(extension_id)
        sources = getattr(policy, directive, [])
        if "'none'" in sources:
            return False
        if "'self'" in sources and source == "'self'":
            return True
        return source in sources or "*" in sources
