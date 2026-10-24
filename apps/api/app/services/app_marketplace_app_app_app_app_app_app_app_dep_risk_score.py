"""Dependency risk scorer — score services by dependency risk factors."""
from __future__ import annotations


def score_risk(service: dict) -> dict:
    dep_count = len(service.get("dependencies", []))
    has_single_point = service.get("single_point_of_failure", False)
    no_fallback = not service.get("has_fallback", False)
    external_deps = service.get("external_dependencies", 0)
    score = dep_count * 5 + (30 if has_single_point else 0) + (20 if no_fallback else 0) + external_deps * 10
    level = "critical" if score > 80 else ("high" if score > 50 else ("medium" if score > 20 else "low"))
    return {"service": service["name"], "score": score, "level": level,
            "factors": {"dep_count": dep_count, "single_point": has_single_point,
                        "no_fallback": no_fallback, "external_deps": external_deps}}


def rank_services(services: list[dict]) -> list[dict]:
    scored = [score_risk(s) for s in services]
    return sorted(scored, key=lambda s: -s["score"])
