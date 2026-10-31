"""Content hash verifier — verify file/content integrity via SHA-256."""
from __future__ import annotations
import hashlib


def compute_hash(content: str, algorithm: str = "sha256") -> dict:
    h = hashlib.new(algorithm, content.encode())
    return {"hash": h.hexdigest(), "algorithm": algorithm, "size_bytes": len(content.encode())}


def verify_integrity(content: str, expected_hash: str, algorithm: str = "sha256") -> dict:
    actual = hashlib.new(algorithm, content.encode()).hexdigest()
    match = actual == expected_hash
    return {"match": match, "algorithm": algorithm,
            "actual": actual[:16] + "...", "expected": expected_hash[:16] + "..."}


def batch_verify(items: list[dict], algorithm: str = "sha256") -> dict:
    results = []
    for item in items:
        r = verify_integrity(item["content"], item["expected_hash"], algorithm)
        results.append({"name": item["name"], "match": r["match"]})
    passed = sum(1 for r in results if r["match"])
    return {"total": len(items), "passed": passed, "failed": len(items) - passed,
            "all_valid": passed == len(items), "results": results}
