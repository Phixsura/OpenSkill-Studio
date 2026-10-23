"""Search highlight — highlight matching text in search results."""

import re
import html


def highlight_matches(*, text: str, query: str, tag: str = "mark") -> dict:
    if not query.strip():
        return {"highlighted": html.escape(text), "match_count": 0}
    safe_text = html.escape(text)
    safe_query = html.escape(query)
    pattern = re.compile(re.escape(safe_query), re.IGNORECASE)
    matches = pattern.findall(safe_text)
    highlighted = pattern.sub(f"<{tag}>\\g<0></{tag}>", safe_text)
    return {"highlighted": highlighted, "match_count": len(matches), "query": query}


def extract_snippet(*, text: str, query: str, context_chars: int = 80) -> dict:
    lower = text.lower()
    pos = lower.find(query.lower())
    if pos == -1:
        return {"snippet": text[:context_chars * 2] + "...", "found": False}
    start = max(0, pos - context_chars)
    end = min(len(text), pos + len(query) + context_chars)
    snippet = ("..." if start > 0 else "") + text[start:end] + ("..." if end < len(text) else "")
    return {"snippet": snippet, "found": True, "position": pos}
