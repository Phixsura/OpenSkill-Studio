"""Extension Collaboration Hub — developer collaboration on extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class CollabThread:
    thread_id: str
    extension_id: str
    title: str
    author_id: str
    messages: list[dict] = field(default_factory=list)
    status: str = "open"  # open, resolved, locked
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtCollabHubService:
    def __init__(self):
        self._threads: dict[str, CollabThread] = {}
        self._counter = 0

    def create_thread(self, extension_id: str, title: str, author_id: str,
                      message: str, tags: list[str] | None = None) -> CollabThread:
        self._counter += 1
        thread = CollabThread(thread_id=f"thread-{self._counter}",
                              extension_id=extension_id, title=title,
                              author_id=author_id, tags=tags or [])
        thread.messages.append({"author_id": author_id, "content": message,
                                "timestamp": time.time()})
        self._threads[thread.thread_id] = thread
        return thread

    def reply(self, thread_id: str, author_id: str, content: str) -> bool:
        thread = self._threads.get(thread_id)
        if not thread or thread.status == "locked":
            return False
        thread.messages.append({"author_id": author_id, "content": content,
                                "timestamp": time.time()})
        return True

    def resolve(self, thread_id: str) -> bool:
        thread = self._threads.get(thread_id)
        if thread and thread.status == "open":
            thread.status = "resolved"
            return True
        return False

    def get_by_extension(self, extension_id: str, status: str | None = None) -> list[CollabThread]:
        threads = [t for t in self._threads.values() if t.extension_id == extension_id]
        if status:
            threads = [t for t in threads if t.status == status]
        return sorted(threads, key=lambda t: t.created_at, reverse=True)

    def search(self, query: str) -> list[CollabThread]:
        q = query.lower()
        return [t for t in self._threads.values()
                if q in t.title.lower() or any(q in m["content"].lower() for m in t.messages)]
