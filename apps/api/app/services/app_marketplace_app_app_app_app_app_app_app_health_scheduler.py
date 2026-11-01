"""Health check scheduler — schedule and track periodic health checks."""
from __future__ import annotations


INTERVALS = {"30s": 30, "1m": 60, "5m": 300, "15m": 900, "1h": 3600}


def create_check(*, name: str, url: str, interval: str = "1m",
                    expected_status: int = 200, timeout_ms: int = 5000) -> dict:
    interval_sec = INTERVALS.get(interval, 60)
    return {"name": name, "url": url, "interval": interval,
            "interval_sec": interval_sec, "expected_status": expected_status,
            "timeout_ms": timeout_ms, "enabled": True}


def evaluate_check(check: dict, *, status_code: int, latency_ms: int) -> dict:
    ok = status_code == check["expected_status"] and latency_ms < check["timeout_ms"]
    return {"name": check["name"], "healthy": ok, "status_code": status_code,
            "latency_ms": latency_ms, "reason": "ok" if ok else
            "status_mismatch" if status_code != check["expected_status"] else "timeout"}


def summarize_checks(results: list[dict]) -> dict:
    healthy = sum(1 for r in results if r["healthy"])
    return {"total": len(results), "healthy": healthy,
            "unhealthy": len(results) - healthy,
            "all_healthy": healthy == len(results)}
