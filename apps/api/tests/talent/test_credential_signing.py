"""Credential signing service tests — Ed25519 keypair, signing, verification, DID."""

import json

from app.talent.services.credential_signing import (
    build_did_document,
    compute_payload_hash,
    generate_keypair,
    public_key_to_multibase,
    sign_payload,
    verify_signature,
)


class TestKeypairGeneration:
    def test_generate_returns_pem_strings(self):
        private_pem, public_pem = generate_keypair()
        assert "BEGIN PRIVATE KEY" in private_pem
        assert "END PRIVATE KEY" in private_pem
        assert "BEGIN PUBLIC KEY" in public_pem
        assert "END PUBLIC KEY" in public_pem

    def test_generate_unique_each_call(self):
        k1_priv, k1_pub = generate_keypair()
        k2_priv, k2_pub = generate_keypair()
        assert k1_priv != k2_priv
        assert k1_pub != k2_pub


class TestSignAndVerify:
    def test_sign_verify_roundtrip(self):
        private_pem, public_pem = generate_keypair()
        payload = json.dumps({"test": "data", "number": 42})
        signature = sign_payload(payload, private_pem)
        assert isinstance(signature, str)
        assert len(signature) > 0
        assert verify_signature(payload, signature, public_pem)

    def test_invalid_signature_rejected(self):
        private_pem, public_pem = generate_keypair()
        payload = json.dumps({"test": "data"})
        signature = sign_payload(payload, private_pem)
        # Tamper with payload
        assert not verify_signature('{"test":"tampered"}', signature, public_pem)

    def test_wrong_key_rejected(self):
        priv1, _pub1 = generate_keypair()
        _priv2, pub2 = generate_keypair()
        payload = json.dumps({"test": "data"})
        signature = sign_payload(payload, priv1)
        assert not verify_signature(payload, signature, pub2)

    def test_empty_payload(self):
        private_pem, public_pem = generate_keypair()
        payload = ""
        signature = sign_payload(payload, private_pem)
        assert verify_signature(payload, signature, public_pem)

    def test_large_payload(self):
        private_pem, public_pem = generate_keypair()
        payload = json.dumps({"data": "x" * 10000})
        signature = sign_payload(payload, private_pem)
        assert verify_signature(payload, signature, public_pem)

    def test_unicode_payload(self):
        private_pem, public_pem = generate_keypair()
        payload = json.dumps({"name": "技能护照", "emoji": "🎓"})
        signature = sign_payload(payload, private_pem)
        assert verify_signature(payload, signature, public_pem)

    def test_corrupted_signature_rejected(self):
        private_pem, public_pem = generate_keypair()
        payload = json.dumps({"test": "data"})
        assert not verify_signature(payload, "not-a-real-signature", public_pem)

    def test_invalid_public_key_rejected(self):
        private_pem, _public_pem = generate_keypair()
        payload = json.dumps({"test": "data"})
        signature = sign_payload(payload, private_pem)
        assert not verify_signature(payload, signature, "not-a-pem-key")


class TestPayloadHash:
    def test_deterministic(self):
        payload = json.dumps({"a": 1})
        h1 = compute_payload_hash(payload)
        h2 = compute_payload_hash(payload)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_different_payloads_different_hashes(self):
        h1 = compute_payload_hash("aaa")
        h2 = compute_payload_hash("bbb")
        assert h1 != h2


class TestMultibase:
    def test_starts_with_z(self):
        _priv, pub = generate_keypair()
        mb = public_key_to_multibase(pub)
        assert mb.startswith("z")
        assert len(mb) > 10


class TestDIDDocument:
    def test_structure(self):
        _priv, pub = generate_keypair()
        doc = build_did_document("org123", pub)

        assert doc["id"] == "did:web:openskill.studio:orgs:org123"
        assert "@context" in doc
        assert "https://www.w3.org/ns/did/v1" in doc["@context"]

        # Verification method
        assert len(doc["verificationMethod"]) == 1
        vm = doc["verificationMethod"][0]
        assert vm["id"] == "did:web:openskill.studio:orgs:org123#key-1"
        assert vm["type"] == "Ed25519VerificationKey2020"
        assert vm["controller"] == doc["id"]
        assert vm["publicKeyMultibase"].startswith("z")

        # Authentication + assertion
        assert "did:web:openskill.studio:orgs:org123#key-1" in doc["authentication"]
        assert "did:web:openskill.studio:orgs:org123#key-1" in doc["assertionMethod"]

    def test_different_orgs_different_dids(self):
        _priv, pub = generate_keypair()
        doc1 = build_did_document("org1", pub)
        doc2 = build_did_document("org2", pub)
        assert doc1["id"] != doc2["id"]
