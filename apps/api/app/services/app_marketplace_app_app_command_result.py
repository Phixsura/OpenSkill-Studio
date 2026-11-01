"""Command result — format CLI command execution results."""


def format_command_result(*, command: str, exit_code: int, stdout: str,
                            stderr: str, duration_ms: int) -> dict:
    success = exit_code == 0
    output_lines = stdout.strip().split("\n") if stdout.strip() else []
    error_lines = stderr.strip().split("\n") if stderr.strip() else []
    return {
        "command": command,
        "exit_code": exit_code,
        "success": success,
        "stdout_lines": output_lines,
        "stderr_lines": error_lines,
        "output_line_count": len(output_lines),
        "error_line_count": len(error_lines),
        "duration_ms": duration_ms,
        "duration_formatted": f"{duration_ms / 1000:.1f}s" if duration_ms >= 1000 else f"{duration_ms}ms",
    }
