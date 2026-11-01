"""Secret scanner — detect leaked secrets in code and configs."""
from __future__ import annotations
import re

PATTERNS = [
    {"name": "aws_key", "regex": r"AKIA[0-9A-Z]{16}", "severity": "critical"},
    {"name": "github_token", "regex": r"gh[pousr]_[A-Za-z0-9_]{36,}", "severity": "critical"},
    {"name": "private_key", "regex": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "severity": "critical"},
    {"name": "generic_secret", "regex": r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9+/=]{16,}['\"]", "severity": "high"},
    {"name": "jwt", "regex": r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "severity": "high"},
]


def scan_content(content: str, *, filename: str = "") -> dict:
    findings = []
    for pat in PATTERNS:
        for m in re.finditer(pat["regex"], content):
            start = content.rfind("\n", 0, m.start()) + 1
            line_num = content[:m.start()].count("\n") + 1
            findings.append({
                "type": pat["name"], "severity": pat["severity"],
                "line": line_num, "file": filename,
                "match_preview": m.group()[:8] + "••••",
            })
    findings.sort(key=lambda f: {"critical": 0, "high": 1, "medium": 2}[f["severity"]])
    return {"file": filename, "findings": findings, "count": len(findings),
            "has_secrets": len(findings) > 0,
            "highest_severity": findings[0]["severity"] if findings else None}


def scan_files(files: dict[str, str]) -> dict:
    all_findings = []
    for fname, content in files.items():
        r = scan_content(content, filename=fname)
        all_findings.extend(r["findings"])
    return {"total_files": len(files), "total_findings": len(all_findings),
            "findings": all_findings, "clean": len(all_findings) == 0}
