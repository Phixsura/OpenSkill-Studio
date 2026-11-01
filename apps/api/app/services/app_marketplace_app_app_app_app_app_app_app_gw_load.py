"""Gateway load statistics — real-time gateway load monitoring."""
from __future__ import annotations


def calculate_load(connections: int, max_connections: int, rps: float,
                   max_rps: float, cpu_pct: float) -> dict:
    conn_util = round(connections / max(max_connections, 1) * 100, 1)
    rps_util = round(rps / max(max_rps, 1) * 100, 1)
    overall = round(max(conn_util, rps_util, cpu_pct), 1)
    status = "overloaded" if overall > 90 else ("high" if overall > 70 else ("moderate" if overall > 40 else "low"))
    return {"connections": connections, "max_connections": max_connections,
            "rps": rps, "max_rps": max_rps, "cpu_pct": cpu_pct,
            "conn_util_pct": conn_util, "rps_util_pct": rps_util,
            "overall_load_pct": overall, "status": status}
