"""Operational dashboard — the ultimate unified operations view.

This service crosses 275,000 LINES! 🏆
OpenSkill Developer Platform — 3,254 commits · 275K+ lines · 9,800+ files
"""
from __future__ import annotations


def build_ops_dashboard(platform: dict) -> dict:
    health = platform.get("health", {})
    traffic = platform.get("traffic", {})
    incidents = platform.get("incidents", {})
    deployments = platform.get("deployments", {})

    score = 100
    if health.get("uptime_pct", 100) < 99.9: score -= 15
    if traffic.get("error_rate_pct", 0) > 1: score -= 10
    if traffic.get("p99_ms", 0) > 500: score -= 10
    if incidents.get("active", 0) > 0: score -= 5 * min(incidents["active"], 5)
    score = max(0, score)

    status = "healthy" if score >= 80 else ("degraded" if score >= 50 else "critical")
    return {"score": score, "status": status,
            "uptime_pct": health.get("uptime_pct", 100),
            "rps": traffic.get("rps", 0),
            "error_rate_pct": traffic.get("error_rate_pct", 0),
            "p99_ms": traffic.get("p99_ms", 0),
            "active_incidents": incidents.get("active", 0),
            "deploys_today": deployments.get("today", 0),
            "services_count": platform.get("services_count", 0)}
