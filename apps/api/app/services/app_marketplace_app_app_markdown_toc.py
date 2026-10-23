"""Markdown TOC — extract table of contents from markdown headings."""

import re
import html


def extract_toc(*, markdown: str) -> dict:
    heading_re = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    items = []
    for match in heading_re.finditer(markdown):
        level = len(match.group(1))
        text = match.group(2).strip()
        slug = re.sub(r"[^\w\s-]", "", text.lower()).replace(" ", "-")
        items.append({"level": level, "text": html.escape(text), "slug": slug})
    max_depth = max((i["level"] for i in items), default=0)
    return {"items": items, "count": len(items), "max_depth": max_depth}
