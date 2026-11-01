"""Content Integrity Verifier — hash-based tamper detection for pack releases and app versions.

Provides supply-chain integrity for the developer platform:
- SHA-256 content hashing for files, archives, and manifests
- Hash chain: each release references the previous release hash
- Tamper detection: verify stored hash matches recomputed hash
- Manifest hash: canonical JSON hash of the manifest for signing
- Batch verification of release histories
- Merkle-style summary hash for multi-file bundles
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class VerifyStatus(str, Enum):
    VALID = "valid"
    TAMPERED = "tampered"
    MISSING_HASH = "missing_hash"
    CHAIN_BROKEN = "chain_broken"


@dataclass
class HashRecord:
    """A hash record for a versioned artifact."""

    artifact_id: str
    version: str
    content_hash: str            # SHA-256 of the content
    manifest_hash: str | None    # SHA-256 of canonical manifest JSON
    previous_hash: str | None    # hash chain: references prior version's content_hash
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class VerifyResult:
    """Result of verifying a single artifact."""

    artifact_id: str
    version: str
    status: VerifyStatus
    expected_hash: str
    actual_hash: str | None
    details: str


@dataclass
class ChainVerifyResult:
    """Result of verifying an entire hash chain."""

    artifact_id: str
    total_versions: int
    valid_count: int
    broken_at: str | None  # version where chain broke
    results: list[VerifyResult]


def sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_string(text: str) -> str:
    """Compute SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(obj: dict) -> str:
    """Compute SHA-256 of canonical JSON (sorted keys, no whitespace)."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_string(canonical)


def merkle_hash(hashes: list[str]) -> str:
    """Compute a Merkle-style summary hash from a list of file hashes.

    Pairs adjacent hashes and hashes them together, level by level.
    If odd count, the last hash is promoted. Returns a single root hash.
    """
    if not hashes:
        return sha256_string("")
    if len(hashes) == 1:
        return hashes[0]

    level = list(hashes)
    while len(level) > 1:
        next_level: list[str] = []
        for i in range(0, len(level), 2):
            if i + 1 < len(level):
                combined = level[i] + level[i + 1]
                next_level.append(sha256_string(combined))
            else:
                next_level.append(level[i])  # odd one out, promote
        level = next_level
    return level[0]


class ContentIntegrityVerifier:
    """Manage and verify content hashes for artifact releases."""

    def __init__(self):
        # (artifact_id, version) → HashRecord
        self._records: dict[tuple[str, str], HashRecord] = {}
        # artifact_id → ordered list of versions
        self._version_order: dict[str, list[str]] = {}

    def record(self, artifact_id: str, version: str, content: bytes,
               manifest: dict | None = None) -> HashRecord:
        """Record a new release with its content hash and optional manifest hash.

        Automatically chains to the previous version's content_hash.
        """
        content_hash = sha256_bytes(content)
        manifest_hash = sha256_json(manifest) if manifest else None

        # Get previous version's hash for chaining
        versions = self._version_order.get(artifact_id, [])
        previous_hash = None
        if versions:
            prev_key = (artifact_id, versions[-1])
            prev_record = self._records.get(prev_key)
            if prev_record:
                previous_hash = prev_record.content_hash

        record = HashRecord(
            artifact_id=artifact_id,
            version=version,
            content_hash=content_hash,
            manifest_hash=manifest_hash,
            previous_hash=previous_hash,
        )
        self._records[(artifact_id, version)] = record
        self._version_order.setdefault(artifact_id, []).append(version)

        log.info(
            "integrity.recorded",
            artifact_id=artifact_id,
            version=version,
            content_hash=content_hash[:16] + "...",
        )
        return record

    def verify(self, artifact_id: str, version: str, content: bytes) -> VerifyResult:
        """Verify content matches the recorded hash."""
        key = (artifact_id, version)
        record = self._records.get(key)

        if record is None:
            return VerifyResult(
                artifact_id=artifact_id,
                version=version,
                status=VerifyStatus.MISSING_HASH,
                expected_hash="",
                actual_hash=None,
                details="No hash record found for this version",
            )

        actual_hash = sha256_bytes(content)
        if actual_hash == record.content_hash:
            return VerifyResult(
                artifact_id=artifact_id,
                version=version,
                status=VerifyStatus.VALID,
                expected_hash=record.content_hash,
                actual_hash=actual_hash,
                details="Content hash matches",
            )
        else:
            log.warning(
                "integrity.tampered",
                artifact_id=artifact_id,
                version=version,
                expected=record.content_hash[:16],
                actual=actual_hash[:16],
            )
            return VerifyResult(
                artifact_id=artifact_id,
                version=version,
                status=VerifyStatus.TAMPERED,
                expected_hash=record.content_hash,
                actual_hash=actual_hash,
                details="Content hash mismatch — possible tampering",
            )

    def verify_manifest(self, artifact_id: str, version: str, manifest: dict) -> VerifyResult:
        """Verify a manifest matches the recorded manifest hash."""
        key = (artifact_id, version)
        record = self._records.get(key)

        if record is None or record.manifest_hash is None:
            return VerifyResult(
                artifact_id=artifact_id, version=version,
                status=VerifyStatus.MISSING_HASH,
                expected_hash="", actual_hash=None,
                details="No manifest hash recorded",
            )

        actual = sha256_json(manifest)
        if actual == record.manifest_hash:
            return VerifyResult(
                artifact_id=artifact_id, version=version,
                status=VerifyStatus.VALID,
                expected_hash=record.manifest_hash, actual_hash=actual,
                details="Manifest hash matches",
            )
        return VerifyResult(
            artifact_id=artifact_id, version=version,
            status=VerifyStatus.TAMPERED,
            expected_hash=record.manifest_hash, actual_hash=actual,
            details="Manifest hash mismatch",
        )

    def verify_chain(self, artifact_id: str) -> ChainVerifyResult:
        """Verify the entire hash chain for an artifact's release history."""
        versions = self._version_order.get(artifact_id, [])
        results: list[VerifyResult] = []
        broken_at: str | None = None
        valid_count = 0

        for i, version in enumerate(versions):
            record = self._records.get((artifact_id, version))
            if record is None:
                results.append(VerifyResult(
                    artifact_id=artifact_id, version=version,
                    status=VerifyStatus.MISSING_HASH,
                    expected_hash="", actual_hash=None,
                    details="Missing hash record",
                ))
                if broken_at is None:
                    broken_at = version
                continue

            if i == 0:
                # First version should have no previous_hash
                if record.previous_hash is None:
                    results.append(VerifyResult(
                        artifact_id=artifact_id, version=version,
                        status=VerifyStatus.VALID,
                        expected_hash=record.content_hash,
                        actual_hash=record.content_hash,
                        details="Chain root — valid",
                    ))
                    valid_count += 1
                else:
                    results.append(VerifyResult(
                        artifact_id=artifact_id, version=version,
                        status=VerifyStatus.CHAIN_BROKEN,
                        expected_hash="null",
                        actual_hash=record.previous_hash,
                        details="First version should not have previous_hash",
                    ))
                    if broken_at is None:
                        broken_at = version
            else:
                # Check that previous_hash matches prior version's content_hash
                prev_record = self._records.get((artifact_id, versions[i - 1]))
                expected_prev = prev_record.content_hash if prev_record else None

                if record.previous_hash == expected_prev:
                    results.append(VerifyResult(
                        artifact_id=artifact_id, version=version,
                        status=VerifyStatus.VALID,
                        expected_hash=expected_prev or "",
                        actual_hash=record.previous_hash or "",
                        details="Chain link valid",
                    ))
                    valid_count += 1
                else:
                    results.append(VerifyResult(
                        artifact_id=artifact_id, version=version,
                        status=VerifyStatus.CHAIN_BROKEN,
                        expected_hash=expected_prev or "",
                        actual_hash=record.previous_hash or "",
                        details="Chain break: previous_hash doesn't match prior version",
                    ))
                    if broken_at is None:
                        broken_at = version

        return ChainVerifyResult(
            artifact_id=artifact_id,
            total_versions=len(versions),
            valid_count=valid_count,
            broken_at=broken_at,
            results=results,
        )

    def get_record(self, artifact_id: str, version: str) -> HashRecord | None:
        return self._records.get((artifact_id, version))

    def list_versions(self, artifact_id: str) -> list[str]:
        return list(self._version_order.get(artifact_id, []))
