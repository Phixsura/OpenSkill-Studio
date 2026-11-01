"""Tests for Content Integrity Verifier — hashing, tamper detection, hash chains, Merkle."""

import pytest

from app.services.content_integrity_verifier import (
    ContentIntegrityVerifier,
    VerifyStatus,
    merkle_hash,
    sha256_bytes,
    sha256_json,
    sha256_string,
)


class TestHashFunctions:
    def test_sha256_bytes_deterministic(self):
        assert sha256_bytes(b"hello") == sha256_bytes(b"hello")

    def test_sha256_bytes_different_input(self):
        assert sha256_bytes(b"hello") != sha256_bytes(b"world")

    def test_sha256_bytes_hex_length(self):
        assert len(sha256_bytes(b"test")) == 64

    def test_sha256_string(self):
        assert sha256_string("hello") == sha256_bytes(b"hello")

    def test_sha256_json_canonical(self):
        # Different key order should produce same hash
        h1 = sha256_json({"b": 2, "a": 1})
        h2 = sha256_json({"a": 1, "b": 2})
        assert h1 == h2

    def test_sha256_json_different_values(self):
        assert sha256_json({"x": 1}) != sha256_json({"x": 2})


class TestMerkleHash:
    def test_empty_list(self):
        h = merkle_hash([])
        assert len(h) == 64  # still a valid hash

    def test_single_hash(self):
        h = merkle_hash(["abc123"])
        assert h == "abc123"

    def test_two_hashes(self):
        h = merkle_hash(["aaa", "bbb"])
        assert h == sha256_string("aaabbb")

    def test_deterministic(self):
        hashes = [sha256_bytes(f"file{i}".encode()) for i in range(5)]
        assert merkle_hash(hashes) == merkle_hash(hashes)

    def test_order_matters(self):
        h1 = merkle_hash(["aaa", "bbb"])
        h2 = merkle_hash(["bbb", "aaa"])
        assert h1 != h2

    def test_odd_count_promotes_last(self):
        h3 = merkle_hash(["a", "b", "c"])
        # "c" is promoted: hash(hash(a+b), c)
        assert len(h3) == 64


class TestRecordAndVerify:
    def test_record_creates_hash(self):
        v = ContentIntegrityVerifier()
        rec = v.record("pack-1", "1.0.0", b"content data")
        assert rec.content_hash == sha256_bytes(b"content data")
        assert rec.previous_hash is None

    def test_record_with_manifest(self):
        v = ContentIntegrityVerifier()
        manifest = {"name": "test", "version": "1.0.0"}
        rec = v.record("pack-1", "1.0.0", b"data", manifest=manifest)
        assert rec.manifest_hash == sha256_json(manifest)

    def test_verify_valid(self):
        v = ContentIntegrityVerifier()
        v.record("pack-1", "1.0.0", b"original content")
        result = v.verify("pack-1", "1.0.0", b"original content")
        assert result.status == VerifyStatus.VALID

    def test_verify_tampered(self):
        v = ContentIntegrityVerifier()
        v.record("pack-1", "1.0.0", b"original content")
        result = v.verify("pack-1", "1.0.0", b"modified content")
        assert result.status == VerifyStatus.TAMPERED
        assert result.actual_hash != result.expected_hash

    def test_verify_missing(self):
        v = ContentIntegrityVerifier()
        result = v.verify("nonexistent", "1.0.0", b"data")
        assert result.status == VerifyStatus.MISSING_HASH

    def test_verify_manifest_valid(self):
        v = ContentIntegrityVerifier()
        manifest = {"name": "test"}
        v.record("pack-1", "1.0.0", b"data", manifest=manifest)
        result = v.verify_manifest("pack-1", "1.0.0", {"name": "test"})
        assert result.status == VerifyStatus.VALID

    def test_verify_manifest_tampered(self):
        v = ContentIntegrityVerifier()
        v.record("pack-1", "1.0.0", b"data", manifest={"name": "test"})
        result = v.verify_manifest("pack-1", "1.0.0", {"name": "hacked"})
        assert result.status == VerifyStatus.TAMPERED

    def test_verify_manifest_missing(self):
        v = ContentIntegrityVerifier()
        v.record("pack-1", "1.0.0", b"data")  # no manifest
        result = v.verify_manifest("pack-1", "1.0.0", {"name": "test"})
        assert result.status == VerifyStatus.MISSING_HASH


class TestHashChain:
    def test_chain_builds_automatically(self):
        v = ContentIntegrityVerifier()
        r1 = v.record("pack-1", "1.0.0", b"v1 content")
        r2 = v.record("pack-1", "2.0.0", b"v2 content")
        r3 = v.record("pack-1", "3.0.0", b"v3 content")
        assert r1.previous_hash is None
        assert r2.previous_hash == r1.content_hash
        assert r3.previous_hash == r2.content_hash

    def test_verify_chain_valid(self):
        v = ContentIntegrityVerifier()
        v.record("pack-1", "1.0.0", b"v1")
        v.record("pack-1", "2.0.0", b"v2")
        v.record("pack-1", "3.0.0", b"v3")
        chain = v.verify_chain("pack-1")
        assert chain.total_versions == 3
        assert chain.valid_count == 3
        assert chain.broken_at is None

    def test_verify_chain_detects_break(self):
        v = ContentIntegrityVerifier()
        v.record("pack-1", "1.0.0", b"v1")
        v.record("pack-1", "2.0.0", b"v2")
        # Manually corrupt the chain
        rec = v._records[("pack-1", "2.0.0")]
        rec.previous_hash = "corrupted_hash_value"
        chain = v.verify_chain("pack-1")
        assert chain.broken_at == "2.0.0"
        assert chain.valid_count == 1  # only v1 is valid

    def test_verify_chain_empty(self):
        v = ContentIntegrityVerifier()
        chain = v.verify_chain("nonexistent")
        assert chain.total_versions == 0
        assert chain.valid_count == 0

    def test_different_artifacts_independent_chains(self):
        v = ContentIntegrityVerifier()
        v.record("pack-a", "1.0.0", b"a-v1")
        v.record("pack-b", "1.0.0", b"b-v1")
        rec_a = v.get_record("pack-a", "1.0.0")
        rec_b = v.get_record("pack-b", "1.0.0")
        assert rec_a.previous_hash is None
        assert rec_b.previous_hash is None


class TestListVersions:
    def test_list_versions_ordered(self):
        v = ContentIntegrityVerifier()
        v.record("pack-1", "1.0.0", b"v1")
        v.record("pack-1", "2.0.0", b"v2")
        v.record("pack-1", "3.0.0", b"v3")
        assert v.list_versions("pack-1") == ["1.0.0", "2.0.0", "3.0.0"]

    def test_list_versions_empty(self):
        v = ContentIntegrityVerifier()
        assert v.list_versions("nonexistent") == []

    def test_get_record(self):
        v = ContentIntegrityVerifier()
        v.record("pack-1", "1.0.0", b"data")
        rec = v.get_record("pack-1", "1.0.0")
        assert rec is not None
        assert rec.artifact_id == "pack-1"

    def test_get_record_missing(self):
        v = ContentIntegrityVerifier()
        assert v.get_record("x", "y") is None
