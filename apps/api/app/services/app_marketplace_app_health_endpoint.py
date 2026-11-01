"""Health endpoint — simple health check response."""
from datetime import datetime, timezone
def health_check() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat(), "version": "16.0.0"}
