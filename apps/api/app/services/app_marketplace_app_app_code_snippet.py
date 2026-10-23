"""Code snippet — syntax-highlighted code block builder."""

import html

LANG_ICONS = {"python": "🐍", "typescript": "📘", "javascript": "📒",
              "bash": "💻", "json": "📋", "yaml": "⚙️", "sql": "🗃️"}


def build_code_snippet(*, code: str, language: str = "text",
                        title: str | None = None, line_numbers: bool = True) -> dict:
    lines = code.splitlines()
    numbered = [{"number": i + 1, "content": html.escape(line)} for i, line in enumerate(lines)]
    return {
        "language": language,
        "icon": LANG_ICONS.get(language, "📄"),
        "title": html.escape(title) if title else None,
        "lines": numbered,
        "line_count": len(lines),
        "show_line_numbers": line_numbers,
        "char_count": len(code),
    }
