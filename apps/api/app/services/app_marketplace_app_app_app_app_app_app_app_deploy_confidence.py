"""Deployment confidence scorer — score confidence based on pre-deploy signals."""
from __future__ import annotations


def score_confidence(signals: dict) -> dict:
    score = 0
    factors = {}
    # Tests passing
    tests = signals.get("tests_passing_pct", 0)
    factors["tests"] = min(25, round(tests / 100 * 25))
    score += factors["tests"]
    # Code coverage
    coverage = signals.get("code_coverage_pct", 0)
    factors["coverage"] = min(15, round(coverage / 100 * 15))
    score += factors["coverage"]
    # No security issues
    sec_issues = signals.get("security_issues", 0)
    factors["security"] = 20 if sec_issues == 0 else max(0, 20 - sec_issues * 5)
    score += factors["security"]
    # Canary healthy
    factors["canary"] = 20 if signals.get("canary_healthy") else 0
    score += factors["canary"]
    # Peer reviewed
    factors["review"] = 10 if signals.get("peer_reviewed") else 0
    score += factors["review"]
    # Rollback plan
    factors["rollback"] = 10 if signals.get("rollback_plan") else 0
    score += factors["rollback"]
    level = "high" if score >= 80 else ("medium" if score >= 50 else "low")
    return {"score": min(score, 100), "level": level, "factors": factors}
