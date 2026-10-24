"""Secret leak detector — scan for exposed secrets in code and configs."""
from __future__ import annotations
import re

PATTERNS = [
    {"name": "aws_key", "pattern": r"AKIA[0-9A-Z]{16}", "severity": "critical"},
    {"name": "github_token", "pattern": r"ghp_[a-zA-Z0-9]{36}", "severity": "critical"},
    {"name": "jwt_secret", "pattern": r"(?i)jwt[_-]?secret\s*[=:]\s*['\"][^'\"]{8,}", "severity": "high"},
    {"name": "password", "pattern": r"(?i)password\s*[=:]\s*['\"][^'\"]{4,}", "severity": "high"},
    {"name": "api_key", "pattern": r"(?i)api[_-]?key\s*[=:]\s*['\"][^'\"]{8,}", "severity": "medium"},
]


def scan_for_secrets(content: str, filename: str = "") -> dict:
    findings = []
    for p in PATTERNS:
        matches = re.findall(p["pattern"], content)
        for m in matches:
            findings.append({"type": p["name"], "severity": p["severity"],
                              "file": filename, "match_preview": m[:20] + "..."})
    critical = sum(1 for f in findings if f["severity"] == "critical")
    return {"findings": findings, "finding_count": len(findings),
            "critical": critical, "clean": len(findings) == 0}


def scan_summary(results: list[dict]) -> dict:
    total = sum(r["finding_count"] for r in results)
    clean = sum(1 for r in results if r["clean"])
    return {"files_scanned": len(results), "clean_files": clean,
            "total_findings": total, "pass": total == 0}
