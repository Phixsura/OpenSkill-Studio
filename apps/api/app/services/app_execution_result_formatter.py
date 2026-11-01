"""Execution result formatter — standardize sandbox execution results."""

def format_execution_result(*, success: bool, output: dict | None = None, error: str | None = None,
                            duration_ms: int = 0, memory_mb: float = 0, logs: list | None = None) -> dict:
    return {
        "success": success,
        "output": output,
        "error": error,
        "duration_ms": duration_ms,
        "memory_mb": round(memory_mb, 1),
        "log_count": len(logs or []),
        "status": "completed" if success else "failed",
    }


def summarize_executions(results: list[dict]) -> dict:
    total = len(results)
    if total == 0:
        return {"total": 0, "success": 0, "failed": 0, "avg_duration_ms": 0, "success_rate": 100.0}
    success = sum(1 for r in results if r.get("success"))
    durations = [r.get("duration_ms", 0) for r in results]
    return {
        "total": total, "success": success, "failed": total - success,
        "avg_duration_ms": round(sum(durations) / total, 1),
        "success_rate": round(success / total * 100, 1),
    }
