"""Open Badges 3.0 export tests — structure and constants."""

from app.talent.services.openbadges import OB3_CONTEXT


class TestOB3Constants:
    def test_context_has_credentials_v1(self):
        assert any("credentials/v1" in c for c in OB3_CONTEXT)

    def test_context_has_ob3(self):
        assert any("ob/v3p0" in c for c in OB3_CONTEXT)

    def test_context_length(self):
        assert len(OB3_CONTEXT) == 2


class TestOB3ExportFunction:
    def test_function_exists(self):
        from app.talent.services.openbadges import export_credential_as_ob3
        assert callable(export_credential_as_ob3)

    def test_function_signature(self):
        import inspect

        from app.talent.services.openbadges import export_credential_as_ob3
        sig = inspect.signature(export_credential_as_ob3)
        params = set(sig.parameters.keys())
        assert "credential_id" in params
        assert "credential_type" in params
        assert "capabilities" in params
        assert "org_id" in params
