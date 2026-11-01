"""Config template engine — render config templates with variable substitution."""
from __future__ import annotations
import re
import html


def render_template(template: str, variables: dict[str, str]) -> dict:
    result = template
    missing = []
    used = []
    for match in re.finditer(r'\$\{(\w+)\}', template):
        var_name = match.group(1)
        if var_name in variables:
            result = result.replace(f"${{{var_name}}}", html.escape(str(variables[var_name])))
            used.append(var_name)
        else:
            missing.append(var_name)
    return {"rendered": result, "used_variables": sorted(set(used)),
            "missing_variables": sorted(set(missing)),
            "complete": len(missing) == 0}


def validate_template(template: str, required_vars: list[str]) -> dict:
    found = set(re.findall(r'\$\{(\w+)\}', template))
    missing = sorted(set(required_vars) - found)
    extra = sorted(found - set(required_vars))
    return {"valid": len(missing) == 0, "missing": missing, "extra": extra,
            "variables_found": sorted(found)}
