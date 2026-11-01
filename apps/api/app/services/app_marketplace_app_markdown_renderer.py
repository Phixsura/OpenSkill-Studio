"""Markdown renderer — safe markdown to HTML conversion."""

import html
import re


def render_markdown(*, text: str) -> dict:
    safe = html.escape(text)
    # Headers
    safe = re.sub(r"^### (.+)$", r"<h3>\1</h3>", safe, flags=re.MULTILINE)
    safe = re.sub(r"^## (.+)$", r"<h2>\1</h2>", safe, flags=re.MULTILINE)
    safe = re.sub(r"^# (.+)$", r"<h1>\1</h1>", safe, flags=re.MULTILINE)
    # Bold and italic
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"\*(.+?)\*", r"<em>\1</em>", safe)
    # Code
    safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
    # Links
    def _safe_link(m):
        label, url = m.group(1), m.group(2).strip()
        if not re.match(r"^(https?://|mailto:|/|#)", html.unescape(url), re.I):
            return label
        return f'<a href="{url}" rel="noopener noreferrer nofollow">{label}</a>'
    safe = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _safe_link, safe)
    # Lists
    safe = re.sub(r"^- (.+)$", r"<li>\1</li>", safe, flags=re.MULTILINE)
    # Paragraphs
    lines = safe.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("<"):
            result.append(f"<p>{stripped}</p>")
        else:
            result.append(stripped)
    return {"html": "\n".join(result), "char_count": len(text), "safe": True}


def extract_headings(*, text: str) -> dict:
    headings = []
    for match in re.finditer(r"^(#{1,3})\s+(.+)$", text, re.MULTILINE):
        level = len(match.group(1))
        headings.append({"level": level, "text": match.group(2), "id": re.sub(r"[^a-z0-9-]", "", match.group(2).lower().replace(" ", "-"))})
    return {"headings": headings, "total": len(headings)}
