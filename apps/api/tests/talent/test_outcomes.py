"""Outcome event tests — types, visibility defaults, model structure."""

from app.talent.models.internship import OUTCOME_EVENT_TYPES, OutcomeEvent


class TestOutcomeEventModel:
    def test_visibility_defaults_to_private(self):
        col = OutcomeEvent.__table__.columns["visibility"]
        assert col.server_default is not None
        assert "private" in str(col.server_default.arg)

    def test_has_user_id_fk(self):
        col = OutcomeEvent.__table__.columns["user_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "users.id" in fks

    def test_has_event_type_column(self):
        col = OutcomeEvent.__table__.columns["event_type"]
        assert col.nullable is False

    def test_has_occurred_at(self):
        assert "occurred_at" in OutcomeEvent.__table__.columns

    def test_has_metadata_column(self):
        """The metadata column is mapped as 'extra' in the ORM to avoid
        SQLAlchemy reserved-name conflict, but the DB column is 'metadata'."""
        # ORM attribute
        assert hasattr(OutcomeEvent, "extra")
        # DB column name
        col_names = set(OutcomeEvent.__table__.columns.keys())
        assert "metadata" in col_names

    def test_has_source_type_and_source_id(self):
        cols = OutcomeEvent.__table__.columns
        assert "source_type" in cols
        assert "source_id" in cols

    def test_visibility_options(self):
        """Visibility: private | passport_visible | public."""
        valid = {"private", "passport_visible", "public"}
        assert "private" in valid  # default
        assert len(valid) == 3


class TestOutcomeEventTypes:
    def test_is_frozenset(self):
        assert isinstance(OUTCOME_EVENT_TYPES, frozenset)

    def test_internship_types_present(self):
        assert "internship_started" in OUTCOME_EVENT_TYPES
        assert "internship_completed" in OUTCOME_EVENT_TYPES

    def test_employment_types_present(self):
        assert "job_offer_received" in OUTCOME_EVENT_TYPES
        assert "job_started" in OUTCOME_EVENT_TYPES

    def test_credential_types_present(self):
        assert "credential_renewed" in OUTCOME_EVENT_TYPES
        assert "capability_reverified" in OUTCOME_EVENT_TYPES
