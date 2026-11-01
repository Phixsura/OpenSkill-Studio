"""API Compatibility Checker — verify backward compatibility between API versions.

Implements:
- Endpoint diff (added/removed/changed)
- Parameter compatibility (new required params = breaking)
- Response schema compatibility (removed fields = breaking)
- HTTP method changes
- Deprecation detection
- Compatibility score
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ApiEndpoint:
    path: str
    method: str
    params: dict[str, dict] = field(default_factory=dict)  # {name: {type, required}}
    response_fields: list[str] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class CompatIssue:
    severity: str  # breaking, warning, info
    category: str  # endpoint, parameter, response, deprecation
    path: str
    message: str


class ApiCompatCheckerService:
    def check(self, old_api: list[ApiEndpoint],
              new_api: list[ApiEndpoint]) -> dict:
        """Compare two API versions for backward compatibility."""
        issues: list[CompatIssue] = []

        old_map = {(e.path, e.method): e for e in old_api}
        new_map = {(e.path, e.method): e for e in new_api}

        old_keys = set(old_map.keys())
        new_keys = set(new_map.keys())

        # Removed endpoints = breaking
        for key in old_keys - new_keys:
            issues.append(CompatIssue(
                "breaking", "endpoint", f"{key[1]} {key[0]}",
                f"Endpoint removed: {key[1]} {key[0]}"))

        # Added endpoints = info
        for key in new_keys - old_keys:
            issues.append(CompatIssue(
                "info", "endpoint", f"{key[1]} {key[0]}",
                f"New endpoint: {key[1]} {key[0]}"))

        # Changed endpoints
        for key in old_keys & new_keys:
            old_ep = old_map[key]
            new_ep = new_map[key]
            self._check_params(old_ep, new_ep, issues)
            self._check_response(old_ep, new_ep, issues)
            self._check_deprecation(old_ep, new_ep, issues)

        breaking = [i for i in issues if i.severity == "breaking"]
        warnings = [i for i in issues if i.severity == "warning"]

        total_endpoints = len(old_keys | new_keys)
        breaking_pct = len(breaking) / max(1, total_endpoints) * 100

        return {
            "compatible": len(breaking) == 0,
            "issues": [{"severity": i.severity, "category": i.category,
                         "path": i.path, "message": i.message} for i in issues],
            "breaking_count": len(breaking),
            "warning_count": len(warnings),
            "score": round(100 - breaking_pct, 1),
            "summary": self._summary(issues),
        }

    def _check_params(self, old: ApiEndpoint, new: ApiEndpoint,
                      issues: list[CompatIssue]) -> None:
        path = f"{old.method} {old.path}"

        for name, info in new.params.items():
            if name not in old.params and info.get("required"):
                issues.append(CompatIssue(
                    "breaking", "parameter", path,
                    f"New required parameter: {name}"))
            elif name not in old.params:
                issues.append(CompatIssue(
                    "info", "parameter", path,
                    f"New optional parameter: {name}"))

        for name in old.params:
            if name not in new.params:
                issues.append(CompatIssue(
                    "warning", "parameter", path,
                    f"Parameter removed: {name}"))

        # Type changes
        for name in set(old.params) & set(new.params):
            old_type = old.params[name].get("type", "")
            new_type = new.params[name].get("type", "")
            if old_type and new_type and old_type != new_type:
                issues.append(CompatIssue(
                    "breaking", "parameter", path,
                    f"Parameter type changed: {name} ({old_type} → {new_type})"))

            # Required change
            was_optional = not old.params[name].get("required", False)
            now_required = new.params[name].get("required", False)
            if was_optional and now_required:
                issues.append(CompatIssue(
                    "breaking", "parameter", path,
                    f"Parameter became required: {name}"))

    def _check_response(self, old: ApiEndpoint, new: ApiEndpoint,
                        issues: list[CompatIssue]) -> None:
        path = f"{old.method} {old.path}"
        removed = set(old.response_fields) - set(new.response_fields)
        for field_name in removed:
            issues.append(CompatIssue(
                "breaking", "response", path,
                f"Response field removed: {field_name}"))

        added = set(new.response_fields) - set(old.response_fields)
        for field_name in added:
            issues.append(CompatIssue(
                "info", "response", path,
                f"New response field: {field_name}"))

    def _check_deprecation(self, old: ApiEndpoint, new: ApiEndpoint,
                           issues: list[CompatIssue]) -> None:
        if not old.deprecated and new.deprecated:
            issues.append(CompatIssue(
                "warning", "deprecation", f"{old.method} {old.path}",
                f"Endpoint deprecated: {old.method} {old.path}"))

    def _summary(self, issues: list[CompatIssue]) -> str:
        breaking = sum(1 for i in issues if i.severity == "breaking")
        if breaking == 0:
            return "✅ Backward compatible"
        return f"❌ {breaking} breaking change(s) detected"
