"""Sandbox debug console — build debug output for sandbox executions."""


def format_debug_output(*, execution_id: str, function_name: str, duration_ms: int, success: bool,
                         logs: list[dict], output: dict | None, error: str | None, env_vars: list[str]) -> dict:
    return {
        "execution_id": execution_id,
        "function_name": function_name,
        "duration_ms": duration_ms,
        "success": success,
        "log_count": len(logs),
        "logs": logs[-50:],  # last 50 logs
        "output": output,
        "error": error,
        "env_vars_injected": len(env_vars),
        "sections": ["logs", "output", "environment", "timeline"],
    }
