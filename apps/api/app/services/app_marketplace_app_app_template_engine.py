"""Template engine — simple variable interpolation with filters."""

import re
import html


FILTERS = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "trim": str.strip,
    "escape": html.escape,
}

VAR_RE = re.compile(r"\{\{\s*(\w+)(?:\s*\|\s*(\w+))?\s*\}\}")


def render_template(*, template: str, variables: dict[str, str]) -> dict:
    missing = []
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        filt = match.group(2)
        if key not in variables:
            missing.append(key)
            return match.group(0)
        val = str(variables[key])
        if filt and filt in FILTERS:
            val = FILTERS[filt](val)
        return val
    output = VAR_RE.sub(replacer, template)
    return {"output": output, "missing": missing, "has_missing": len(missing) > 0,
            "variables_used": list(set(VAR_RE.findall(template)))}
