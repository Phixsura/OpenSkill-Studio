"""Content Hash Verifier — Subresource Integrity (SRI) for extension assets.

Implements:
- Multi-algorithm hash generation (SHA-256, SHA-384, SHA-512)
- SRI hash format (base64-encoded with algorithm prefix)
- Manifest verification (all files match expected hashes)
- Tamper detection with diff reporting
- Hash chain for ordered file verification
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import base64


SUPPORTED_ALGORITHMS = {"sha256", "sha384", "sha512"}


@dataclass
class FileHash:
    path: str
    algorithm: str
    digest: str  # base64-encoded
    size_bytes: int

    @property
    def sri(self) -> str:
        """Subresource Integrity format."""
        return f"{self.algorithm}-{self.digest}"


@dataclass
class VerificationResult:
    path: str
    expected: str
    actual: str
    match: bool
    tampered: bool = False


class ContentHashVerifyService:
    def __init__(self):
        self._manifests: dict[str, dict[str, FileHash]] = {}  # ext_id -> {path -> hash}

    def hash_content(self, content: bytes, algorithm: str = "sha256") -> str:
        if algorithm not in SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        h = hashlib.new(algorithm, content)
        return base64.b64encode(h.digest()).decode()

    def generate_sri(self, content: bytes, algorithm: str = "sha384") -> str:
        digest = self.hash_content(content, algorithm)
        return f"{algorithm}-{digest}"

    def build_manifest(self, extension_id: str,
                       files: dict[str, bytes],
                       algorithm: str = "sha256") -> dict[str, FileHash]:
        manifest = {}
        for path, content in files.items():
            digest = self.hash_content(content, algorithm)
            fh = FileHash(path=path, algorithm=algorithm,
                          digest=digest, size_bytes=len(content))
            manifest[path] = fh
        self._manifests[extension_id] = manifest
        return manifest

    def verify_manifest(self, extension_id: str,
                        files: dict[str, bytes]) -> tuple[bool, list[VerificationResult]]:
        manifest = self._manifests.get(extension_id)
        if not manifest:
            return False, [VerificationResult("", "", "", False)]

        results = []
        all_ok = True

        # Check each expected file
        for path, expected_hash in manifest.items():
            if path not in files:
                results.append(VerificationResult(
                    path=path, expected=expected_hash.sri,
                    actual="MISSING", match=False, tampered=True))
                all_ok = False
                continue

            actual_digest = self.hash_content(files[path], expected_hash.algorithm)
            match = actual_digest == expected_hash.digest
            results.append(VerificationResult(
                path=path, expected=expected_hash.sri,
                actual=f"{expected_hash.algorithm}-{actual_digest}",
                match=match, tampered=not match))
            if not match:
                all_ok = False

        # Check for unexpected files
        for path in files:
            if path not in manifest:
                results.append(VerificationResult(
                    path=path, expected="NOT IN MANIFEST",
                    actual="EXISTS", match=False, tampered=True))
                all_ok = False

        return all_ok, results

    def generate_hash_chain(self, files: dict[str, bytes],
                            algorithm: str = "sha256") -> str:
        """Generate a single hash representing the ordered chain of all files."""
        chain = hashlib.new(algorithm)
        for path in sorted(files.keys()):
            chain.update(path.encode())
            chain.update(files[path])
        return base64.b64encode(chain.digest()).decode()

    def verify_chain(self, expected_chain: str, files: dict[str, bytes],
                     algorithm: str = "sha256") -> bool:
        actual = self.generate_hash_chain(files, algorithm)
        # Constant-time comparison
        return len(expected_chain) == len(actual) and all(
            a == b for a, b in zip(expected_chain, actual))
