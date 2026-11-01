"""Content Addressable Store — store/retrieve objects by content hash.

Like Git's object store: content → SHA-256 → address.
Same content always gets same address. Deduplication is automatic.

Implements:
- Store by content hash (SHA-256)
- Automatic deduplication (same content = same address)
- Reference counting for garbage collection
- Verify integrity on read
- Bulk store with manifest
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field


@dataclass
class CasObject:
    address: str  # SHA-256 hash
    content: bytes
    size: int
    ref_count: int = 1
    content_type: str = "application/octet-stream"


class CasStoreService:
    def __init__(self):
        self._objects: dict[str, CasObject] = {}
        self._total_stored = 0
        self._total_deduped = 0

    def _hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def store(self, content: bytes, content_type: str = "application/octet-stream") -> str:
        """Store content, return its address (hash). Deduplicates automatically."""
        address = self._hash(content)
        if address in self._objects:
            self._objects[address].ref_count += 1
            self._total_deduped += 1
            return address

        self._objects[address] = CasObject(
            address=address, content=content, size=len(content),
            content_type=content_type)
        self._total_stored += 1
        return address

    def retrieve(self, address: str, verify: bool = True) -> bytes | None:
        """Retrieve content by address. Optionally verify integrity."""
        obj = self._objects.get(address)
        if not obj:
            return None
        if verify:
            actual_hash = self._hash(obj.content)
            if actual_hash != address:
                raise ValueError(f"Integrity check failed: expected {address}, got {actual_hash}")
        return obj.content

    def exists(self, address: str) -> bool:
        return address in self._objects

    def get_metadata(self, address: str) -> dict | None:
        obj = self._objects.get(address)
        if not obj:
            return None
        return {"address": obj.address, "size": obj.size,
                "ref_count": obj.ref_count, "content_type": obj.content_type}

    def release(self, address: str) -> bool:
        """Decrement ref count. Remove when zero."""
        obj = self._objects.get(address)
        if not obj:
            return False
        obj.ref_count -= 1
        if obj.ref_count <= 0:
            del self._objects[address]
        return True

    def store_manifest(self, files: dict[str, bytes]) -> dict[str, str]:
        """Store multiple files, return {filename: address} mapping."""
        manifest = {}
        for name, content in files.items():
            manifest[name] = self.store(content)
        return manifest

    def gc(self) -> int:
        """Remove objects with zero references."""
        to_remove = [addr for addr, obj in self._objects.items() if obj.ref_count <= 0]
        for addr in to_remove:
            del self._objects[addr]
        return len(to_remove)

    def stats(self) -> dict:
        total_size = sum(obj.size for obj in self._objects.values())
        return {
            "objects": len(self._objects),
            "total_bytes": total_size,
            "total_stored": self._total_stored,
            "total_deduped": self._total_deduped,
            "dedup_ratio": round(self._total_deduped / max(1, self._total_stored + self._total_deduped) * 100, 1),
        }
