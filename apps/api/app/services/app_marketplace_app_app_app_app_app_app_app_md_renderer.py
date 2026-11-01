"""Markdown renderer — convert markdown to structured content blocks."""
from __future__ import annotations
import re
import html


def render_markdown(text: str) -> dict:
    blocks = []
    lines = text.strip().split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # Headings
        m = re.match(r"^(#{1,6})\s+(.+)", line)
        if m:
            blocks.append({"type": "heading", "level": len(m.group(1)),
                           "text": html.escape(m.group(2))})
            i += 1; continue
        # Code blocks
        if line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({"type": "code", "language": lang, "code": "\n".join(code_lines)})
            i += 1; continue
        # Empty
        if not line.strip():
            i += 1; continue
        # Paragraph
        blocks.append({"type": "paragraph", "text": html.escape(line)})
        i += 1
    return {"blocks": blocks, "block_count": len(blocks),
            "word_count": len(text.split()),
            "read_time_min": max(1, len(text.split()) // 200)}
