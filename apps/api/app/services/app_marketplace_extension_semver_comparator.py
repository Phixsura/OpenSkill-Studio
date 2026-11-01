"""Semantic Version Comparator — full semver 2.0 comparison and range matching.

Implements:
- Parse semver strings with pre-release and build metadata
- Compare versions with proper pre-release ordering
- Version range matching (>=, <, ^, ~, ||, -)
- Sort version lists
- Find latest matching version from a list
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re
from functools import total_ordering

SEMVER_RE = re.compile(
    r'^v?(\d+)\.(\d+)\.(\d+)'
    r'(?:-([\w.]+))?'      # pre-release
    r'(?:\+([\w.]+))?$'    # build metadata
)


@total_ordering
@dataclass
class SemVer:
    major: int
    minor: int
    patch: int
    prerelease: str = ""
    build: str = ""

    @classmethod
    def parse(cls, version: str) -> SemVer | None:
        m = SEMVER_RE.match(version.strip())
        if not m:
            return None
        return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                   m.group(4) or "", m.group(5) or "")

    @property
    def tuple(self) -> tuple:
        return (self.major, self.minor, self.patch)

    def __eq__(self, other):
        if not isinstance(other, SemVer):
            return NotImplemented
        return self.tuple == other.tuple and self.prerelease == other.prerelease

    def __lt__(self, other):
        if not isinstance(other, SemVer):
            return NotImplemented
        if self.tuple != other.tuple:
            return self.tuple < other.tuple
        # Pre-release has lower precedence than release
        if self.prerelease and not other.prerelease:
            return True  # 1.0.0-alpha < 1.0.0
        if not self.prerelease and other.prerelease:
            return False
        # Compare pre-release identifiers
        return self._compare_prerelease(self.prerelease, other.prerelease) < 0

    @staticmethod
    def _compare_prerelease(a: str, b: str) -> int:
        if not a and not b:
            return 0
        a_parts = a.split(".")
        b_parts = b.split(".")
        for ap, bp in zip(a_parts, b_parts):
            a_num = ap.isdigit()
            b_num = bp.isdigit()
            if a_num and b_num:
                diff = int(ap) - int(bp)
                if diff != 0:
                    return diff
            elif a_num:
                return -1  # numeric < string
            elif b_num:
                return 1
            else:
                if ap < bp: return -1
                if ap > bp: return 1
        return len(a_parts) - len(b_parts)

    def __str__(self) -> str:
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            s += f"-{self.prerelease}"
        if self.build:
            s += f"+{self.build}"
        return s

    def __hash__(self):
        return hash((self.major, self.minor, self.patch, self.prerelease))


class SemVerComparatorService:
    def parse(self, version: str) -> SemVer | None:
        return SemVer.parse(version)

    def compare(self, a: str, b: str) -> int:
        """Returns -1, 0, or 1."""
        va, vb = SemVer.parse(a), SemVer.parse(b)
        if not va or not vb:
            raise ValueError(f"Invalid version: {a if not va else b}")
        if va < vb: return -1
        if va == vb: return 0
        return 1

    def sort_versions(self, versions: list[str]) -> list[str]:
        parsed = [(v, SemVer.parse(v)) for v in versions]
        valid = [(v, sv) for v, sv in parsed if sv is not None]
        valid.sort(key=lambda x: x[1])
        return [v for v, _ in valid]

    def latest(self, versions: list[str], include_prerelease: bool = False) -> str | None:
        parsed = [(v, SemVer.parse(v)) for v in versions]
        valid = [(v, sv) for v, sv in parsed if sv is not None]
        if not include_prerelease:
            valid = [(v, sv) for v, sv in valid if not sv.prerelease]
        if not valid:
            return None
        return max(valid, key=lambda x: x[1])[0]

    def satisfies_range(self, version: str, range_str: str) -> bool:
        """Check if version satisfies a simple range constraint."""
        sv = SemVer.parse(version)
        if not sv:
            return False

        # Handle OR ranges (||)
        if "||" in range_str:
            return any(self.satisfies_range(version, r.strip())
                       for r in range_str.split("||"))

        # Handle compound ranges (space-separated = AND)
        parts = range_str.strip().split()
        if len(parts) > 1 and not parts[0].startswith(("^", "~")):
            return all(self._check_single(sv, p) for p in parts)

        return self._check_single(sv, range_str.strip())

    def _check_single(self, sv: SemVer, constraint: str) -> bool:
        from app.services.app_marketplace_extension_dep_conflict import version_satisfies
        return version_satisfies(str(sv), constraint)

    def diff(self, a: str, b: str) -> str:
        """Returns what changed: major, minor, patch, prerelease, or equal."""
        va, vb = SemVer.parse(a), SemVer.parse(b)
        if not va or not vb:
            return "invalid"
        if va == vb:
            return "equal"
        if va.major != vb.major:
            return "major"
        if va.minor != vb.minor:
            return "minor"
        if va.patch != vb.patch:
            return "patch"
        return "prerelease"
