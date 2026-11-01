"""Playground output — code execution output formatter."""

import html
import re


def format_output(*, stdout: str, stderr: str, exit_code: int,
                    execution_ms: int) -> dict:
    stdout_lines = stdout.splitlines()
    stderr_lines = stderr.splitlines()
    has_error = exit_code != 0 or len(stderr_lines) > 0
    return {
        "stdout": html.escape(stdout),
        "stderr": html.escape(stderr),
        "stdout_lines": len(stdout_lines),
        "stderr_lines": len(stderr_lines),
        "exit_code": exit_code,
        "success": exit_code == 0,
        "has_error": has_error,
        "execution_ms": execution_ms,
        "total_output_bytes": len(stdout.encode()) + len(stderr.encode()),
    }


def detect_language_errors(*, output: str, language: str) -> list[dict]:
    patterns = {
        "python": [
            (re.compile(r"(\w+Error): (.+)"), "runtime_error"),
            (re.compile(r"SyntaxError: (.+)"), "syntax_error"),
            (re.compile(r"File \"(.+)\", line (\d+)"), "traceback"),
        ],
        "javascript": [
            (re.compile(r"(\w+Error): (.+)"), "runtime_error"),
            (re.compile(r"SyntaxError: (.+)"), "syntax_error"),
        ],
    }
    errors = []
    for pattern, err_type in patterns.get(language, []):
        for m in pattern.finditer(output):
            errors.append({"type": err_type, "message": html.escape(m.group(0)),
                           "position": m.start()})
    return errors
