"""Extension Status Page — public status page for extension services."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class ServiceStatus:
    name: str
    status: str = "operational"  # operational, degraded, partial_outage, major_outage, maintenance
    uptime_pct: float = 100.0
    last_checked: float = 0.0


@dataclass
class StatusPage:
    extension_id: str
    title: str
    services: list[ServiceStatus] = field(default_factory=list)
    overall: str = "operational"
    updated_at: float = 0.0


class ExtStatusPageService:
    STATUS_PRIORITY = {"major_outage": 0, "partial_outage": 1, "degraded": 2, "maintenance": 3, "operational": 4}

    def __init__(self):
        self._pages: dict[str, StatusPage] = {}

    def create(self, extension_id: str, title: str, services: list[str]) -> StatusPage:
        page = StatusPage(extension_id=extension_id, title=title,
                          services=[ServiceStatus(name=s) for s in services],
                          updated_at=time.time())
        self._pages[extension_id] = page
        return page

    def update_service(self, extension_id: str, service_name: str,
                       status: str, uptime_pct: float = 100.0) -> bool:
        page = self._pages.get(extension_id)
        if not page: return False
        for svc in page.services:
            if svc.name == service_name:
                svc.status = status
                svc.uptime_pct = uptime_pct
                svc.last_checked = time.time()
                self._recalc_overall(page)
                return True
        return False

    def _recalc_overall(self, page: StatusPage) -> None:
        if not page.services:
            page.overall = "operational"
            return
        worst = min(page.services, key=lambda s: self.STATUS_PRIORITY.get(s.status, 4))
        page.overall = worst.status
        page.updated_at = time.time()

    def get(self, extension_id: str) -> StatusPage | None:
        return self._pages.get(extension_id)

    def get_uptime_summary(self, extension_id: str) -> dict:
        page = self._pages.get(extension_id)
        if not page: return {}
        avg_uptime = sum(s.uptime_pct for s in page.services) / len(page.services) if page.services else 0
        return {"overall": page.overall, "avg_uptime": round(avg_uptime, 2),
                "service_count": len(page.services)}
