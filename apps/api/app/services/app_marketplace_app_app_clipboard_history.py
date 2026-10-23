"""Clipboard history — recent copy/paste tracking for developer tools."""

import html
from datetime import datetime, timezone
from collections import deque


class ClipboardHistory:
    def __init__(self, *, max_size: int = 50):
        self._items: deque[dict] = deque(maxlen=max_size)
        self.max_size = max_size

    def add(self, *, content: str, source: str = "manual") -> dict:
        preview = content[:100] + ("..." if len(content) > 100 else "")
        entry = {"content": content, "preview": html.escape(preview),
                 "source": source, "char_count": len(content),
                 "timestamp": datetime.now(timezone.utc).isoformat()}
        self._items.appendleft(entry)
        return entry

    def list_items(self, *, limit: int = 10) -> dict:
        items = list(self._items)[:limit]
        return {"items": items, "total": len(self._items), "max_size": self.max_size}

    def search(self, *, query: str) -> list[dict]:
        q = query.lower()
        return [i for i in self._items if q in i["content"].lower()]

    def clear(self) -> dict:
        count = len(self._items)
        self._items.clear()
        return {"cleared": count}
