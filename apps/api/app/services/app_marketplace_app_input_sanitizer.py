"""Input sanitizer — prevent XSS, SQL injection, and command injection in app inputs."""

import re
import html


def sanitize_html_input(*, value: str) -> str:
    """Escape HTML entities to prevent XSS."""
    return html.escape(value, quote=True)


def detect_sql_injection(*, value: str) -> dict:
    patterns = [r"('\s*(OR|AND)\s+')", r"(;\s*(DROP|DELETE|UPDATE|INSERT))", r"(UNION\s+SELECT)",
                r"(--\s*$)", r"(/\*.*\*/)", r"('\s*=\s*')"]
    for p in patterns:
        if re.search(p, value, re.IGNORECASE):
            return {"safe": False, "pattern": p, "input": value[:50]}
    return {"safe": True, "pattern": None, "input": value[:50]}


def detect_command_injection(*, value: str) -> dict:
    dangerous = ["|", ";", "`", "$(", "&&", "||", ">", "<", "\n"]
    found = [d for d in dangerous if d in value]
    return {"safe": len(found) == 0, "dangerous_chars": found}


def sanitize_filename(*, filename: str) -> str:
    # Remove path separators and null bytes
    clean = filename.replace("/", "").replace("\\", "").replace("\x00", "")
    clean = re.sub(r'[^\w.\-]', '_', clean)
    # Prevent directory traversal
    clean = clean.lstrip(".")
    return clean or "unnamed"
