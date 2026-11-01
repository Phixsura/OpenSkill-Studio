"""String utils — text processing utilities for marketplace."""

import re
import html


def slugify(*, text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def truncate(*, text: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rsplit(" ", 1)[0] + suffix


def word_count(*, text: str) -> dict:
    words = text.split()
    chars = len(text)
    sentences = len(re.findall(r"[.!?]+", text))
    return {"words": len(words), "characters": chars, "sentences": max(sentences, 1 if words else 0),
            "reading_time_min": max(1, round(len(words) / 200))}


def highlight_matches(*, text: str, query: str) -> str:
    if not query:
        return html.escape(text)
    escaped = html.escape(text)
    pattern = re.compile(re.escape(html.escape(query)), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", escaped)
