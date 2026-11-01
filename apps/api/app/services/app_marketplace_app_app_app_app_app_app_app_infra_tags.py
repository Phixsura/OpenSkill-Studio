"""Infrastructure tag manager — enforce tagging policies on resources."""
from __future__ import annotations

REQUIRED_TAGS = {"env", "team", "cost_center", "service"}


def validate_tags(resource_name: str, tags: dict[str, str]) -> dict:
    missing = sorted(REQUIRED_TAGS - set(tags.keys()))
    extra = sorted(set(tags.keys()) - REQUIRED_TAGS)
    return {"resource": resource_name, "tags": tags,
            "missing": missing, "compliant": len(missing) == 0,
            "tag_count": len(tags), "extra_tags": extra}


def tag_compliance_report(resources: list[dict]) -> dict:
    results = [validate_tags(r["name"], r.get("tags", {})) for r in resources]
    compliant = sum(1 for r in results if r["compliant"])
    return {"total": len(results), "compliant": compliant,
            "non_compliant": len(results) - compliant,
            "compliance_pct": round(compliant / max(len(results), 1) * 100)}


def suggest_tags(resource_name: str, resource_type: str) -> dict:
    suggestions = {"env": "production", "team": "platform",
                    "cost_center": "engineering", "service": resource_name}
    if resource_type == "database":
        suggestions["backup"] = "daily"
    return {"resource": resource_name, "suggested_tags": suggestions}
