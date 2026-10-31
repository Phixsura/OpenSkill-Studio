"""Extension Screenshot Manager — manage listing screenshots and media."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Screenshot:
    screenshot_id: str
    extension_id: str
    url: str
    caption: str = ""
    order: int = 0
    uploaded_at: float = 0.0
    def __post_init__(self):
        if not self.uploaded_at: self.uploaded_at = time.time()


class ExtScreenshotMgrService:
    MAX_SCREENSHOTS = 10
    ALLOWED_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

    def __init__(self):
        self._screenshots: dict[str, list[Screenshot]] = {}  # ext_id -> list
        self._counter = 0

    def upload(self, extension_id: str, url: str, caption: str = "") -> Screenshot:
        ext = url.rsplit(".", 1)[-1].lower() if "." in url else ""
        if f".{ext}" not in self.ALLOWED_TYPES:
            raise ValueError(f"Invalid file type: .{ext}")
        current = self._screenshots.get(extension_id, [])
        if len(current) >= self.MAX_SCREENSHOTS:
            raise ValueError(f"Max {self.MAX_SCREENSHOTS} screenshots")
        self._counter += 1
        ss = Screenshot(screenshot_id=f"ss-{self._counter}", extension_id=extension_id,
                        url=url, caption=caption, order=len(current))
        if extension_id not in self._screenshots:
            self._screenshots[extension_id] = []
        self._screenshots[extension_id].append(ss)
        return ss

    def get_all(self, extension_id: str) -> list[Screenshot]:
        return sorted(self._screenshots.get(extension_id, []), key=lambda s: s.order)

    def reorder(self, extension_id: str, screenshot_ids: list[str]) -> bool:
        screenshots = self._screenshots.get(extension_id, [])
        by_id = {s.screenshot_id: s for s in screenshots}
        for i, sid in enumerate(screenshot_ids):
            if sid in by_id:
                by_id[sid].order = i
        return True

    def delete(self, extension_id: str, screenshot_id: str) -> bool:
        screenshots = self._screenshots.get(extension_id, [])
        for i, s in enumerate(screenshots):
            if s.screenshot_id == screenshot_id:
                screenshots.pop(i)
                return True
        return False
