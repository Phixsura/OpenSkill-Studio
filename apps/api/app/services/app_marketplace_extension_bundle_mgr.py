"""Extension Bundle Manager — group extensions into installable bundles."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class ExtBundle:
    bundle_id: str
    name: str
    description: str
    extensions: list[str] = field(default_factory=list)
    created_by: str = ""
    discount_pct: float = 0.0
    install_count: int = 0
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtBundleMgrService:
    def __init__(self):
        self._bundles: dict[str, ExtBundle] = {}
        self._counter = 0

    def create(self, name: str, description: str, extensions: list[str],
               created_by: str, discount_pct: float = 0) -> ExtBundle:
        if len(extensions) < 2:
            raise ValueError("Bundle must contain at least 2 extensions")
        if discount_pct < 0 or discount_pct > 50:
            raise ValueError("Discount must be 0-50%")
        self._counter += 1
        b = ExtBundle(bundle_id=f"bnd-{self._counter}", name=name,
                      description=description, extensions=extensions,
                      created_by=created_by, discount_pct=discount_pct)
        self._bundles[b.bundle_id] = b
        return b

    def install(self, bundle_id: str) -> list[str] | None:
        b = self._bundles.get(bundle_id)
        if not b: return None
        b.install_count += 1
        return list(b.extensions)

    def get_containing(self, extension_id: str) -> list[ExtBundle]:
        return [b for b in self._bundles.values() if extension_id in b.extensions]

    def get_popular(self, limit: int = 10) -> list[ExtBundle]:
        return sorted(self._bundles.values(), key=lambda b: b.install_count, reverse=True)[:limit]

    def get_all(self) -> list[ExtBundle]:
        return list(self._bundles.values())
