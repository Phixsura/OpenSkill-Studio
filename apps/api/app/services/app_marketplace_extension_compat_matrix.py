"""Extension Compatibility Matrix — track platform version compatibility."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CompatEntry:
    extension_id: str
    ext_version: str
    platform_version: str
    status: str = "compatible"  # compatible, incompatible, untested, deprecated


class ExtCompatMatrixService:
    def __init__(self):
        self._matrix: dict[str, list[CompatEntry]] = {}  # ext_id -> entries

    def set(self, extension_id: str, ext_version: str,
            platform_version: str, status: str) -> CompatEntry:
        entry = CompatEntry(extension_id=extension_id, ext_version=ext_version,
                            platform_version=platform_version, status=status)
        if extension_id not in self._matrix:
            self._matrix[extension_id] = []
        # Replace if exists
        self._matrix[extension_id] = [
            e for e in self._matrix[extension_id]
            if not (e.ext_version == ext_version and e.platform_version == platform_version)
        ]
        self._matrix[extension_id].append(entry)
        return entry

    def check(self, extension_id: str, ext_version: str,
              platform_version: str) -> str:
        entries = self._matrix.get(extension_id, [])
        for e in entries:
            if e.ext_version == ext_version and e.platform_version == platform_version:
                return e.status
        return "untested"

    def get_compatible_versions(self, extension_id: str,
                                platform_version: str) -> list[str]:
        entries = self._matrix.get(extension_id, [])
        return [e.ext_version for e in entries
                if e.platform_version == platform_version and e.status == "compatible"]

    def get_matrix(self, extension_id: str) -> list[CompatEntry]:
        return self._matrix.get(extension_id, [])
