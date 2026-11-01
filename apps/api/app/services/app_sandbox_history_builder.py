"""Sandbox history builder — compile execution history page data."""

def build_sandbox_history_page(*, executions: list[dict], total: int, page: int, per_page: int,
                                  success_rate: float, avg_duration_ms: float) -> dict:
    return {
        "executions": executions,
        "total": total, "page": page, "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 1,
        "summary": {"success_rate": round(success_rate, 1), "avg_duration_ms": round(avg_duration_ms, 1), "total_executions": total},
    }
