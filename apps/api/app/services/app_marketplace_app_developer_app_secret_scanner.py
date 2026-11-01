"""Secret scanner — detect accidentally committed secrets in app code."""

import re

SECRET_PATTERNS = [
    {"name": "AWS Access Key", "pattern": r"AKIA[0-9A-Z]{16}", "severity": "critical"},
    {"name": "Generic API Key", "pattern": r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"][A-Za-z0-9]{20,}['\"]", "severity": "high"},
    {"name": "Private Key", "pattern": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "severity": "critical"},
    {"name": "JWT Token", "pattern": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "severity": "high"},
    {"name": "Database URL", "pattern": r"(?i)(postgres|mysql|mongodb)://[^\s'\"]+:[^\s'\"]+@", "severity": "critical"},
    {"name": "Bearer Token", "pattern": r"(?i)bearer\s+[A-Za-z0-9_\-.]{20,}", "severity": "medium"},
]


def scan_content(*, content: str, filename: str = "") -> list[dict]:
    findings = []
    for sp in SECRET_PATTERNS:
        matches = re.finditer(sp["pattern"], content)
        for m in matches:
            line_num = content[:m.start()].count("\n") + 1
            findings.append({"type": sp["name"], "severity": sp["severity"],
                              "line": line_num, "file": filename,
                              "match_preview": m.group()[:20] + "..."})
    return findings


def scan_files(*, files: dict[str, str]) -> dict:
    all_findings = []
    for filename, content in files.items():
        findings = scan_content(content=content, filename=filename)
        all_findings.extend(findings)
    critical = sum(1 for f in all_findings if f["severity"] == "critical")
    return {"findings": all_findings, "total": len(all_findings), "critical": critical,
            "files_scanned": len(files), "clean": len(all_findings) == 0}
