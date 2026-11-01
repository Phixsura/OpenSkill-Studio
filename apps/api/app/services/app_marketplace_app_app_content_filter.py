"""Content filter — text content moderation and profanity detection."""

import re
import html

BLOCKED_PATTERNS = [
    re.compile(r"\b(spam|scam|phishing)\b", re.I),
    re.compile(r"\b(hack|exploit|malware)\b", re.I),
]

SEVERITY = {"spam": "high", "scam": "high", "phishing": "critical",
            "hack": "medium", "exploit": "high", "malware": "critical"}


def check_content(*, text: str) -> dict:
    flags = []
    clean = text
    for pattern in BLOCKED_PATTERNS:
        for match in pattern.finditer(text):
            word = match.group(0).lower()
            flags.append({"word": word, "position": match.start(),
                          "severity": SEVERITY.get(word, "low")})
            clean = clean[:match.start()] + "*" * len(match.group(0)) + clean[match.end():]
    max_severity = "none"
    for f in flags:
        if f["severity"] == "critical":
            max_severity = "critical"
            break
        if f["severity"] == "high" and max_severity != "critical":
            max_severity = "high"
        elif f["severity"] == "medium" and max_severity not in ("high", "critical"):
            max_severity = "medium"
    return {"original": html.escape(text), "cleaned": html.escape(clean),
            "flags": flags, "flag_count": len(flags),
            "max_severity": max_severity, "safe": len(flags) == 0}
