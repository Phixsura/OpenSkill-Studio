"""App content hash — deterministic SHA-256 hashing for app bundles.

Produces a content-addressable hash from manifest + source files,
used to verify integrity and detect changes between versions.
"""

import hashlib
import json


def hash_manifest(manifest: dict) -> str:
    """Hash a manifest dict deterministically (sorted JSON)."""
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def hash_content(data: bytes) -> str:
    """Hash raw bytes (source code, bundle)."""
    return hashlib.sha256(data).hexdigest()


def hash_files(files: dict[str, bytes]) -> str:
    """Hash a set of files deterministically.
    
    Files are sorted by path, each contributing path + content hash.
    """
    h = hashlib.sha256()
    for path in sorted(files.keys()):
        h.update(path.encode())
        h.update(b"\x00")
        h.update(hashlib.sha256(files[path]).digest())
    return h.hexdigest()


def verify_content_hash(manifest: dict, expected_hash: str) -> bool:
    """Verify a manifest matches its declared content_hash."""
    return hash_manifest(manifest) == expected_hash


def generate_version_hash(*, manifest: dict, source_hash: str | None = None) -> str:
    """Generate a combined hash for a version (manifest + optional source)."""
    h = hashlib.sha256()
    h.update(hash_manifest(manifest).encode())
    if source_hash:
        h.update(source_hash.encode())
    return h.hexdigest()
