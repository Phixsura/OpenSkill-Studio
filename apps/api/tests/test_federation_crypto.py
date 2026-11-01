"""Tests for federation cryptographic primitives — Ed25519 signing, verification, canonical JSON."""

import json
from datetime import UTC, datetime, timedelta

import pytest

from app.services.federation_crypto import (
    canonical_json,
    compute_key_id,
    generate_ed25519_keypair,
    sign_envelope,
    verify_envelope_signature,
    verify_envelope_with_peer,
)


class TestKeyGeneration:
    def test_generate_keypair_returns_pem_and_key_id(self):
        private_pem, public_pem, key_id = generate_ed25519_keypair()
        assert private_pem.startswith("-----BEGIN PRIVATE KEY-----")
        assert public_pem.startswith("-----BEGIN PUBLIC KEY-----")
        assert key_id.startswith("sha256:")
        assert len(key_id) > 10

    def test_generate_keypair_unique(self):
        _, _, kid1 = generate_ed25519_keypair()
        _, _, kid2 = generate_ed25519_keypair()
        assert kid1 != kid2

    def test_compute_key_id_matches(self):
        _, public_pem, key_id = generate_ed25519_keypair()
        assert compute_key_id(public_pem) == key_id


class TestCanonicalJson:
    def test_sorted_keys(self):
        obj = {"z": 1, "a": 2, "m": 3}
        result = canonical_json(obj)
        assert result == b'{"a":2,"m":3,"z":1}'

    def test_no_whitespace(self):
        obj = {"key": "value", "nested": {"inner": True}}
        result = canonical_json(obj)
        assert b" " not in result
        assert b"\n" not in result

    def test_nested_sorted(self):
        obj = {"b": {"z": 1, "a": 2}, "a": 0}
        result = canonical_json(obj)
        parsed = json.loads(result)
        keys = list(parsed.keys())
        assert keys == ["a", "b"]

    def test_datetime_serialized(self):
        dt = datetime(2026, 10, 27, 10, 0, 0, tzinfo=UTC)
        obj = {"time": dt}
        result = canonical_json(obj)
        assert b"2026-10-27" in result

    def test_deterministic(self):
        obj = {"x": [1, 2, 3], "a": {"nested": True}}
        assert canonical_json(obj) == canonical_json(obj)


class TestSignAndVerify:
    def test_sign_and_verify_roundtrip(self):
        private_pem, public_pem, key_id = generate_ed25519_keypair()
        envelope = sign_envelope(
            payload={"name": "test-pack", "version": "1.0.0"},
            envelope_type="registry_artifact",
            instance_uri="https://test.openskill.io",
            signing_key_pem=private_pem,
            key_id=key_id,
        )

        assert envelope["envelope_version"] == "1.0"
        assert envelope["envelope_type"] == "registry_artifact"
        assert envelope["source_instance"] == "https://test.openskill.io"
        assert envelope["source_key_id"] == key_id
        assert "signature" in envelope
        assert "envelope_id" in envelope

        assert verify_envelope_signature(envelope, public_pem) is True

    def test_tampered_payload_fails(self):
        private_pem, public_pem, key_id = generate_ed25519_keypair()
        envelope = sign_envelope(
            payload={"name": "test-pack"},
            envelope_type="registry_artifact",
            instance_uri="https://test.openskill.io",
            signing_key_pem=private_pem,
            key_id=key_id,
        )

        # Tamper with the payload
        envelope["payload"]["name"] = "evil-pack"
        assert verify_envelope_signature(envelope, public_pem) is False

    def test_wrong_key_fails(self):
        private_pem, _, key_id = generate_ed25519_keypair()
        _, other_public_pem, _ = generate_ed25519_keypair()

        envelope = sign_envelope(
            payload={"name": "test"},
            envelope_type="registry_artifact",
            instance_uri="https://test.openskill.io",
            signing_key_pem=private_pem,
            key_id=key_id,
        )

        assert verify_envelope_signature(envelope, other_public_pem) is False

    def test_missing_signature_fails(self):
        assert verify_envelope_signature({"no": "sig"}, "fake") is False

    def test_invalid_base64_signature_fails(self):
        _, public_pem, _ = generate_ed25519_keypair()
        assert verify_envelope_signature({"signature": "!!!invalid!!!"}, public_pem) is False

    def test_sign_with_expires_at(self):
        private_pem, public_pem, key_id = generate_ed25519_keypair()
        expires = datetime.now(UTC) + timedelta(days=30)
        envelope = sign_envelope(
            payload={"name": "test"},
            envelope_type="registry_artifact",
            instance_uri="https://test.openskill.io",
            signing_key_pem=private_pem,
            key_id=key_id,
            expires_at=expires,
        )
        assert "expires_at" in envelope
        assert verify_envelope_signature(envelope, public_pem) is True


class TestVerifyWithPeer:
    def test_current_key_matches(self):
        private_pem, public_pem, key_id = generate_ed25519_keypair()
        envelope = sign_envelope(
            payload={"test": True},
            envelope_type="registry_artifact",
            instance_uri="https://a.openskill.io",
            signing_key_pem=private_pem,
            key_id=key_id,
        )

        assert verify_envelope_with_peer(
            envelope=envelope,
            peer_key_id=key_id,
            peer_public_key_pem=public_pem,
        ) is True

    def test_previous_key_within_grace(self):
        old_priv, old_pub, old_kid = generate_ed25519_keypair()
        _, new_pub, new_kid = generate_ed25519_keypair()

        # Envelope signed with old key
        envelope = sign_envelope(
            payload={"test": True},
            envelope_type="registry_artifact",
            instance_uri="https://a.openskill.io",
            signing_key_pem=old_priv,
            key_id=old_kid,
        )

        # Peer has rotated to new key; old key is in grace period
        assert verify_envelope_with_peer(
            envelope=envelope,
            peer_key_id=new_kid,
            peer_public_key_pem=new_pub,
            peer_previous_key_id=old_kid,
            peer_previous_key_pem=old_pub,
            peer_previous_key_expires_at=datetime.now(UTC) + timedelta(days=30),
        ) is True

    def test_previous_key_expired_fails(self):
        old_priv, old_pub, old_kid = generate_ed25519_keypair()
        _, new_pub, new_kid = generate_ed25519_keypair()

        envelope = sign_envelope(
            payload={"test": True},
            envelope_type="registry_artifact",
            instance_uri="https://a.openskill.io",
            signing_key_pem=old_priv,
            key_id=old_kid,
        )

        # Grace period has expired
        assert verify_envelope_with_peer(
            envelope=envelope,
            peer_key_id=new_kid,
            peer_public_key_pem=new_pub,
            peer_previous_key_id=old_kid,
            peer_previous_key_pem=old_pub,
            peer_previous_key_expires_at=datetime.now(UTC) - timedelta(days=1),
        ) is False

    def test_unknown_key_id_fails(self):
        private_pem, _, key_id = generate_ed25519_keypair()
        _, pub2, kid2 = generate_ed25519_keypair()

        envelope = sign_envelope(
            payload={"test": True},
            envelope_type="registry_artifact",
            instance_uri="https://a.openskill.io",
            signing_key_pem=private_pem,
            key_id=key_id,
        )

        # Peer has a completely different key
        assert verify_envelope_with_peer(
            envelope=envelope,
            peer_key_id=kid2,
            peer_public_key_pem=pub2,
        ) is False

    def test_missing_source_key_id_fails(self):
        assert verify_envelope_with_peer(
            envelope={"no_source_key_id": True},
            peer_key_id="anything",
            peer_public_key_pem="anything",
        ) is False
