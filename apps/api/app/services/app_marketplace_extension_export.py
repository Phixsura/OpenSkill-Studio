"""Extension Export — export extension packages for distribution.

Builds distributable packages from extension source, metadata,
and assets for publishing to the marketplace.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib


@dataclass
class ExportManifest:
    extension_id: str
    version: str
    files: list[str]
    total_size_bytes: int
    checksum: str
    created_at: str = ""
    format: str = "tar.gz"

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class ExtensionExporter:
    """Builds distributable extension packages."""

    MAX_PACKAGE_BYTES = 50 * 1024 * 1024  # 50MB

    def __init__(self):
        self._exports: dict[str, ExportManifest] = {}

    def build_package(self, extension_id: str, version: str,
                      files: dict[str, str | bytes]) -> tuple[ExportManifest | None, str]:
        """Build a package from files. files: {path: content}."""
        if not files:
            return None, "No files to export"

        total_size = sum(
            len(c.encode() if isinstance(c, str) else c) for c in files.values()
        )
        if total_size > self.MAX_PACKAGE_BYTES:
            return None, f"Package too large: {total_size} > {self.MAX_PACKAGE_BYTES}"

        # Validate required files
        has_manifest = any("manifest" in f.lower() for f in files)
        if not has_manifest:
            return None, "Missing manifest file"

        # Calculate checksum
        content_hash = hashlib.sha256()
        for path in sorted(files.keys()):
            content = files[path]
            if isinstance(content, str):
                content = content.encode()
            content_hash.update(path.encode())
            content_hash.update(content)

        manifest = ExportManifest(
            extension_id=extension_id, version=version,
            files=sorted(files.keys()),
            total_size_bytes=total_size,
            checksum=content_hash.hexdigest(),
        )
        key = f"{extension_id}@{version}"
        self._exports[key] = manifest
        return manifest, "Package built"

    def get_manifest(self, extension_id: str, version: str) -> ExportManifest | None:
        return self._exports.get(f"{extension_id}@{version}")

    def verify_checksum(self, extension_id: str, version: str,
                        files: dict[str, str | bytes]) -> bool:
        """Verify package integrity against stored checksum."""
        manifest = self.get_manifest(extension_id, version)
        if not manifest:
            return False
        content_hash = hashlib.sha256()
        for path in sorted(files.keys()):
            content = files[path]
            if isinstance(content, str):
                content = content.encode()
            content_hash.update(path.encode())
            content_hash.update(content)
        return content_hash.hexdigest() == manifest.checksum

    def list_exports(self, extension_id: str) -> list[ExportManifest]:
        return [m for m in self._exports.values() if m.extension_id == extension_id]
