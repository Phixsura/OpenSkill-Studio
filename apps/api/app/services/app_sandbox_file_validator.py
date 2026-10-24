"""Sandbox file validator — validate uploaded app bundles."""

import os

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_FILES = 500
BLOCKED_EXTENSIONS = frozenset({".exe", ".dll", ".so", ".dylib", ".sh", ".bat", ".cmd", ".ps1"})
ALLOWED_EXTENSIONS = frozenset({".js", ".ts", ".py", ".json", ".html", ".css", ".yml", ".yaml", ".md", ".txt", ".svg", ".png", ".jpg"})


def validate_bundle(files: dict[str, int]) -> list[str]:
    """Validate a file bundle. files = {path: size_bytes}."""
    errors = []
    if len(files) > MAX_FILES:
        errors.append(f"Too many files ({len(files)}, max {MAX_FILES})")
    total_size = sum(files.values())
    if total_size > MAX_FILE_SIZE:
        errors.append(f"Bundle too large ({total_size} bytes, max {MAX_FILE_SIZE})")
    for path, size in files.items():
        ext = os.path.splitext(path)[1].lower()
        if ext in BLOCKED_EXTENSIONS:
            errors.append(f"Blocked file type: {path}")
        if ".." in path or path.startswith("/"):
            errors.append(f"Invalid path: {path}")
    return errors
