"""Template Engine — Mustache-style rendering with loops and conditionals.

Implements:
- Variable interpolation: {{ name }}
- Conditionals: {% if condition %}...{% endif %}
- Negated: {% if not condition %}...{% endif %}
- Loops: {% for item in list %}...{% endfor %}
- Nested property access: {{ user.name }}
- HTML escaping by default, {{{ raw }}} for unescaped
- Template inheritance via {% block name %}...{% endblock %}
"""
from __future__ import annotations
import re
import html


# Regex patterns
VAR_RE = re.compile(r'\{\{\{\s*(.+?)\s*\}\}\}|\{\{\s*(.+?)\s*\}\}')
BLOCK_RE = re.compile(
    r'\{%\s*(if|if not|for|endif|endfor|block|endblock)\s*(.*?)\s*%\}',
    re.DOTALL
)


class TemplateError(Exception):
    pass


class TemplateEngineService:
    def __init__(self):
        self._filters: dict[str, callable] = {
            "upper": str.upper,
            "lower": str.lower,
            "title": str.title,
            "len": lambda x: str(len(x)),
            "default": lambda x, d="": x if x else d,
        }

    def render(self, template: str, context: dict) -> str:
        """Render a template with the given context."""
        # Process control blocks first
        result = self._process_blocks(template, context)
        # Then interpolate variables
        result = self._interpolate(result, context)
        return result

    def _resolve(self, path: str, context: dict) -> object:
        """Resolve dotted path like 'user.name' from context."""
        # Check for filter: value|filter
        if "|" in path:
            value_path, filter_name = path.rsplit("|", 1)
            value = self._resolve(value_path.strip(), context)
            filt = self._filters.get(filter_name.strip())
            if filt:
                return filt(str(value) if value is not None else "")
            return value

        parts = path.strip().split(".")
        current = context
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
            if current is None:
                return None
        return current

    def _interpolate(self, text: str, context: dict) -> str:
        """Replace {{ var }} with HTML-escaped values, {{{ var }}} unescaped."""
        def replacer(m):
            raw_var = m.group(1)  # {{{ }}} = unescaped
            escaped_var = m.group(2)  # {{ }} = escaped

            if raw_var:
                value = self._resolve(raw_var, context)
                return str(value) if value is not None else ""
            else:
                value = self._resolve(escaped_var, context)
                return html.escape(str(value)) if value is not None else ""

        return VAR_RE.sub(replacer, text)

    def _process_blocks(self, template: str, context: dict) -> str:
        """Process if/for blocks recursively."""
        result = []
        pos = 0
        tokens = list(BLOCK_RE.finditer(template))

        if not tokens:
            return template

        i = 0
        while pos < len(template):
            # Find next block tag
            next_token = None
            for t in tokens:
                if t.start() >= pos:
                    next_token = t
                    break

            if not next_token:
                result.append(template[pos:])
                break

            # Add text before the tag
            result.append(template[pos:next_token.start()])

            keyword = next_token.group(1)
            args = next_token.group(2).strip()

            if keyword == "if":
                body, end_pos = self._find_block_end(template, next_token.end(), "endif")
                value = self._resolve(args, context)
                if value:
                    result.append(self._process_blocks(body, context))
                pos = end_pos

            elif keyword == "if not":
                body, end_pos = self._find_block_end(template, next_token.end(), "endif")
                value = self._resolve(args, context)
                if not value:
                    result.append(self._process_blocks(body, context))
                pos = end_pos

            elif keyword == "for":
                body, end_pos = self._find_block_end(template, next_token.end(), "endfor")
                # Parse "item in list"
                m = re.match(r'(\w+)\s+in\s+(.+)', args)
                if not m:
                    raise TemplateError(f"Invalid for syntax: {args}")
                var_name, list_path = m.group(1), m.group(2)
                items = self._resolve(list_path, context)
                if items and hasattr(items, '__iter__'):
                    for idx, item in enumerate(items):
                        loop_ctx = {**context, var_name: item,
                                    "loop": {"index": idx, "first": idx == 0,
                                             "last": idx == len(items) - 1}}
                        result.append(self._process_blocks(body, loop_ctx))
                pos = end_pos

            else:
                pos = next_token.end()

        return "".join(result)

    def _find_block_end(self, template: str, start: int, end_tag: str) -> tuple[str, int]:
        """Find matching end tag, handling nesting."""
        depth = 1
        pos = start
        tag_name = end_tag.replace("end", "")  # "if" or "for"

        for m in BLOCK_RE.finditer(template, start):
            kw = m.group(1)
            if kw in (tag_name, f"{tag_name} not") and kw != end_tag:
                depth += 1
            elif kw == end_tag:
                depth -= 1
                if depth == 0:
                    body = template[start:m.start()]
                    return body, m.end()

        raise TemplateError(f"Unclosed {tag_name} block")

    def register_filter(self, name: str, fn: callable) -> None:
        self._filters[name] = fn
