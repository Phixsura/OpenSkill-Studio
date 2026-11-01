"""Secret scanner — detect accidentally committed secrets in code."""

import re


SECRET_PATTERNS = [
    {"name": "AWS Access Key", "pattern": re.compile(r"AKIA[0-9A-Z]{16}"), "severity": "critical"},
    {"name": "GitHub Token", "pattern": re.compile(r"gh[ps]_[A-Za-z0-9_]{36,}"), "severity": "critical"},
    {"name": "Slack Token", "pattern": re.compile(r"xox[baprs]-[0-9a-zA-Z-]{10,}"), "severity": "high"},
    {"name": "Private Key", "pattern": re.compile(r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----"), "severity": "critical"},
    {"name": "Generic API Key", "pattern": re.compile(r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"][a-zA-Z0-9]{20,}['\"]"), "severity": "medium"},
    {"name": "JWT Token", "pattern": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "severity": "high"},
]


def scan_content(*, content: str, filename: str = "") -> dict:
    findings = []
    for sp in SECRET_PATTERNS:
        matches = sp["pattern"].findall(content)
        for match in matches:
            preview = match[:8] + "..." if len(match) > 8 else match
            findings.append({
                "type": sp["name"],
                "severity": sp["severity"],
                "preview": preview,
                "filename": filename,
            })
    return {
        "findings": findings,
        "total": len(findings),
        "has_critical": any(f["severity"] == "critical" for f in findings),
        "clean": len(findings) == 0,
    }
