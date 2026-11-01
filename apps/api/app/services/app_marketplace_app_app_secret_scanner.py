"""Secret scanner — detect leaked secrets in code and config."""

import re
import html

PATTERNS = {
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[ps]_[A-Za-z0-9_]{36,}"),
    "npm_token": re.compile(r"npm_[A-Za-z0-9]{36,}"),
    "private_key": re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
    "generic_secret": re.compile(r"(?i)(password|secret|api_key|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}


def scan_text(*, text: str, filename: str = "") -> dict:
    findings = []
    for secret_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            line_num = text[:match.start()].count("\n") + 1
            findings.append({
                "type": secret_type,
                "line": line_num,
                "preview": html.escape(match.group(0)[:20] + "..." if len(match.group(0)) > 20 else match.group(0)),
                "severity": "critical" if secret_type in ("aws_key", "private_key") else "high",
            })
    return {"filename": html.escape(filename), "findings": findings,
            "count": len(findings), "has_secrets": len(findings) > 0}


def scan_files(*, files: list[dict]) -> dict:
    results = []
    total = 0
    for f in files:
        r = scan_text(text=f.get("content", ""), filename=f.get("name", ""))
        if r["has_secrets"]:
            results.append(r)
            total += r["count"]
    return {"files_scanned": len(files), "files_with_secrets": len(results),
            "total_findings": total, "results": results,
            "clean": total == 0}
