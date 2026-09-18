"""W3C VC and Open Badges 3.0 export tests."""

import json
from datetime import UTC, datetime, timedelta

from app.talent.services.credential_signing import generate_keypair
from app.talent.services.openbadges import (
    OB3_CONTEXT,
    export_credential_as_ob3,
    verify_ob3,
)
from app.talent.services.vc_export import (
    VC_CONTEXT,
    export_passport_as_vc,
    verify_vc,
)


class TestVCExport:
    def _make_snapshot_payload(self):
        return {
            "user_id": "user_01",
            "snapshot_at": datetime.now(UTC).isoformat(),
            "capabilities": [
                {
                    "capability_id": "cap_01",
                    "capability_name": "Python Programming",
                    "level": 3,
                    "level_label": "Independent production",
                    "score": 0.65,
                    "confidence": 0.8,
                    "evidence_count": 5,
                },
                {
                    "capability_id": "cap_02",
                    "capability_name": "Machine Learning",
                    "level": 2,
                    "level_label": "Assisted practice",
                    "score": 0.45,
                    "confidence": 0.6,
                    "evidence_count": 3,
                },
            ],
        }

    def test_vc_has_required_fields(self):
        priv, pub = generate_keypair()
        now = datetime.now(UTC)
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=now,
            expires_at=now + timedelta(days=365),
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
            checksum="abc123",
        )

        # W3C VC required fields
        assert vc["@context"] == VC_CONTEXT
        assert "VerifiableCredential" in vc["type"]
        assert "SkillPassportCredential" in vc["type"]
        assert vc["id"] == "urn:uuid:snap_01"
        assert "issuer" in vc
        assert vc["issuer"]["id"] == "did:web:openskill.studio:orgs:org_01"
        assert "issuanceDate" in vc
        assert "expirationDate" in vc
        assert "credentialSubject" in vc
        assert "proof" in vc

    def test_vc_credential_subject_structure(self):
        priv, pub = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
        )

        subject = vc["credentialSubject"]
        assert subject["id"] == "urn:openskill:user:user_01"
        assert subject["type"] == "SkillPassportHolder"
        assert len(subject["capabilities"]) == 2
        assert subject["capabilities"][0]["capabilityName"] == "Python Programming"
        assert subject["capabilities"][0]["level"] == 3

    def test_vc_no_expiration(self):
        priv, pub = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
        )
        assert "expirationDate" not in vc

    def test_vc_checksum_included(self):
        priv, pub = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
            checksum="deadbeef",
        )
        assert vc["credentialStatus"]["value"] == "deadbeef"

    def test_vc_proof_structure(self):
        priv, pub = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
        )

        proof = vc["proof"]
        assert proof["type"] == "Ed25519Signature2020"
        assert "created" in proof
        assert proof["verificationMethod"] == "did:web:openskill.studio:orgs:org_01#key-1"
        assert proof["proofPurpose"] == "assertionMethod"
        assert "proofValue" in proof
        assert len(proof["proofValue"]) > 10

    def test_vc_sign_verify_roundtrip(self):
        priv, pub = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
        )
        assert verify_vc(vc, pub)

    def test_vc_tampered_fails_verification(self):
        priv, pub = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
        )
        # Tamper with issuer name
        vc["issuer"]["name"] = "Tampered Issuer"
        assert not verify_vc(vc, pub)

    def test_vc_wrong_key_fails(self):
        priv1, _pub1 = generate_keypair()
        _priv2, pub2 = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv1,
            public_key_pem=_pub1,
        )
        assert not verify_vc(vc, pub2)

    def test_vc_empty_capabilities(self):
        priv, pub = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload={"capabilities": []},
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
        )
        assert vc["credentialSubject"]["capabilities"] == []
        assert verify_vc(vc, pub)

    def test_vc_json_serializable(self):
        priv, pub = generate_keypair()
        vc = export_passport_as_vc(
            snapshot_payload=self._make_snapshot_payload(),
            snapshot_id="snap_01",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            public_key_pem=pub,
        )
        serialized = json.dumps(vc)
        deserialized = json.loads(serialized)
        assert deserialized["@context"] == VC_CONTEXT


class TestOB3Export:
    def _make_capabilities(self):
        return [
            {"capability_id": "cap_01", "required_level": 3, "achieved_level": 4},
            {"capability_id": "cap_02", "required_level": 2, "achieved_level": 2},
        ]

    def _make_capability_details(self):
        return [
            {
                "id": "cap_01",
                "canonical_name": "Python Programming",
                "description": "Proficiency in Python programming language",
                "external_ids": {
                    "esco_uri": "http://data.europa.eu/esco/skill/python",
                    "onet_code": "15-1252.00",
                },
            },
            {
                "id": "cap_02",
                "canonical_name": "Data Analysis",
                "description": "Ability to analyze and interpret data",
                "external_ids": {"esco_uri": "http://data.europa.eu/esco/skill/data-analysis"},
            },
        ]

    def test_ob3_has_required_fields(self):
        priv, _pub = generate_keypair()
        now = datetime.now(UTC)
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="python_fundamentals",
            user_id="user_01",
            issued_at=now,
            expires_at=now + timedelta(days=365),
            capabilities=self._make_capabilities(),
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            capability_details=self._make_capability_details(),
        )

        assert ob3["@context"] == OB3_CONTEXT
        assert "VerifiableCredential" in ob3["type"]
        assert "OpenBadgeCredential" in ob3["type"]
        assert ob3["id"] == "urn:uuid:cred_01"
        assert "issuer" in ob3
        assert "Profile" in ob3["issuer"]["type"]
        assert "issuanceDate" in ob3
        assert "expirationDate" in ob3
        assert "credentialSubject" in ob3
        assert "proof" in ob3
        assert "name" in ob3

    def test_ob3_achievement_structure(self):
        priv, _pub = generate_keypair()
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="python_fundamentals",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            capabilities=self._make_capabilities(),
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            capability_details=self._make_capability_details(),
        )

        subject = ob3["credentialSubject"]
        assert "AchievementSubject" in subject["type"]
        achievement = subject["achievement"]
        assert "Achievement" in achievement["type"]
        assert achievement["name"] == "Python Fundamentals"
        assert "criteria" in achievement
        assert "narrative" in achievement["criteria"]

    def test_ob3_esco_alignment(self):
        priv, _pub = generate_keypair()
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="python_fundamentals",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            capabilities=self._make_capabilities(),
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            capability_details=self._make_capability_details(),
        )

        achievement = ob3["credentialSubject"]["achievement"]
        assert "alignment" in achievement
        alignment = achievement["alignment"]

        # Should have ESCO for both caps + O*NET for cap_01
        esco_entries = [a for a in alignment if a["targetFramework"] == "ESCO"]
        onet_entries = [a for a in alignment if a["targetFramework"] == "O*NET"]
        assert len(esco_entries) == 2
        assert len(onet_entries) == 1
        assert esco_entries[0]["targetUrl"] == "http://data.europa.eu/esco/skill/python"
        assert "15-1252.00" in onet_entries[0]["targetUrl"]

    def test_ob3_no_alignment_without_external_ids(self):
        priv, _pub = generate_keypair()
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="basic_skill",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            capabilities=self._make_capabilities(),
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            # No capability_details → no external_ids → no alignment
        )

        achievement = ob3["credentialSubject"]["achievement"]
        assert "alignment" not in achievement

    def test_ob3_sign_verify_roundtrip(self):
        priv, pub = generate_keypair()
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="python_fundamentals",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            capabilities=self._make_capabilities(),
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
        )
        assert verify_ob3(ob3, pub)

    def test_ob3_tampered_fails(self):
        priv, pub = generate_keypair()
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="python_fundamentals",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            capabilities=self._make_capabilities(),
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
        )
        ob3["name"] = "Tampered Name"
        assert not verify_ob3(ob3, pub)

    def test_ob3_criteria_narrative(self):
        priv, _pub = generate_keypair()
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="python_fundamentals",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            capabilities=self._make_capabilities(),
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
            capability_details=self._make_capability_details(),
        )

        narrative = ob3["credentialSubject"]["achievement"]["criteria"]["narrative"]
        assert "Python Programming" in narrative
        assert "level 4" in narrative
        assert "required: 3" in narrative

    def test_ob3_json_serializable(self):
        priv, _pub = generate_keypair()
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="test",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            capabilities=[],
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
        )
        serialized = json.dumps(ob3)
        deserialized = json.loads(serialized)
        assert deserialized["@context"] == OB3_CONTEXT

    def test_ob3_empty_capabilities(self):
        priv, pub = generate_keypair()
        ob3 = export_credential_as_ob3(
            credential_id="cred_01",
            credential_type="empty_badge",
            user_id="user_01",
            issued_at=datetime.now(UTC),
            expires_at=None,
            capabilities=[],
            org_id="org_01",
            signing_key_id="key_01",
            private_key_pem=priv,
        )
        assert verify_ob3(ob3, pub)
        narrative = ob3["credentialSubject"]["achievement"]["criteria"]["narrative"]
        assert "Credential awarded" in narrative
