"""Avatar uploader — validate and process avatar image uploads."""
from __future__ import annotations
import hashlib

ALLOWED_TYPES = (".png", ".jpg", ".jpeg", ".webp")
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
MIN_SIZE_PX = 64
MAX_SIZE_PX = 1024


def validate_avatar(*, filename: str, size_bytes: int,
                      width: int = 0, height: int = 0) -> dict:
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    errors = []
    if ext not in ALLOWED_TYPES:
        errors.append(f"File type {ext} not allowed. Use: {', '.join(ALLOWED_TYPES)}")
    if size_bytes > MAX_SIZE_BYTES:
        errors.append(f"File too large. Max: {MAX_SIZE_BYTES // 1024 // 1024}MB")
    if width > 0 and (width < MIN_SIZE_PX or width > MAX_SIZE_PX):
        errors.append(f"Width must be {MIN_SIZE_PX}-{MAX_SIZE_PX}px")
    if height > 0 and (height < MIN_SIZE_PX or height > MAX_SIZE_PX):
        errors.append(f"Height must be {MIN_SIZE_PX}-{MAX_SIZE_PX}px")
    if width > 0 and height > 0 and abs(width - height) > width * 0.1:
        errors.append("Image should be roughly square")
    return {"valid": len(errors) == 0, "errors": errors, "filename": filename,
            "extension": ext, "size_bytes": size_bytes}


def generate_avatar_url(user_id: str) -> str:
    h = hashlib.md5(user_id.encode()).hexdigest()
    return f"https://cdn.openskill.io/avatars/{h[:2]}/{h}.png"
