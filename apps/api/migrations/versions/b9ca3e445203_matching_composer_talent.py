"""Matching engine + composers + talent tables (Issue #21, ADR-012/013)

Revision ID: b9ca3e445203
Revises: a8b92d334102
Create Date: 2026-08-23 15:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM, JSONB

# revision identifiers, used by Alembic.
revision: str = "b9ca3e445203"
down_revision: str | None = "a8b92d334102"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── requirement_context enum ──
    ENUM(
        "LEARNING", "PRODUCTION", "COMMERCIAL_PROJECT", "TALENT_MATCHING",
        name="requirement_context",
    ).create(op.get_bind(), checkfirst=True)
    requirement_context = ENUM(
        "LEARNING", "PRODUCTION", "COMMERCIAL_PROJECT", "TALENT_MATCHING",
        name="requirement_context", create_type=False,
    )

    # ── requirement_profiles ──
    op.create_table(
        "requirement_profiles",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id", sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "user_id", sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("context_type", requirement_context, nullable=False),
        sa.Column("raw_request", sa.Text(), nullable=True),
        sa.Column("source_brief_id", sa.String(26), nullable=True),
        sa.Column("structured_requirements", JSONB(), nullable=False, server_default="{}"),
        sa.Column("extraction_meta", JSONB(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by", sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index("ix_req_profiles_org", "requirement_profiles", ["org_id", "context_type"])

    # ── matching_configs ──
    op.create_table(
        "matching_configs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("target_entity_type", sa.String(30), nullable=False),
        sa.Column("weights", JSONB(), nullable=False, server_default="{}"),
        sa.Column("thresholds", JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index(
        "uq_matching_config", "matching_configs", ["target_entity_type", "version"], unique=True
    )

    # ── match_runs ──
    op.create_table(
        "match_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id", sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("context_type", sa.String(30), nullable=False),
        sa.Column(
            "requirement_profile_id", sa.String(26),
            sa.ForeignKey("requirement_profiles.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("target_entity_type", sa.String(30), nullable=False),
        sa.Column("engine_version", sa.String(20), nullable=False),
        sa.Column("config_version", sa.Integer(), nullable=False),
        sa.Column("candidate_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("excluded_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_by", sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index("ix_match_runs_org", "match_runs", ["org_id", "created_at"])

    # ── match_results ──
    op.create_table(
        "match_results",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "match_run_id", sa.String(26),
            sa.ForeignKey("match_runs.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("entity_type", sa.String(30), nullable=False),
        sa.Column("entity_id", sa.String(26), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("score", sa.Numeric(5, 4), nullable=True),
        sa.Column("reasons", JSONB(), nullable=False, server_default="[]"),
        sa.Column("gaps", JSONB(), nullable=False, server_default="[]"),
        sa.Column("hard_failures", JSONB(), nullable=False, server_default="[]"),
        sa.Column("tier", sa.String(20), nullable=True),
    )
    op.create_index("ix_matchresults_run", "match_results", ["match_run_id", "rank"])

    # ── feedback_events ──
    op.create_table(
        "feedback_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id", sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("match_run_id", sa.String(26), nullable=True),
        sa.Column("entity_type", sa.String(30), nullable=False),
        sa.Column("entity_id", sa.String(26), nullable=False),
        sa.Column("event_type", sa.String(20), nullable=False),
        sa.Column("rank_position", sa.Integer(), nullable=True),
        sa.Column("score", sa.Numeric(5, 4), nullable=True),
        sa.Column("config_version", sa.Integer(), nullable=True),
        sa.Column(
            "created_by", sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        # R17: rank position at impression time is unrecoverable — enforce it
        sa.CheckConstraint(
            "(event_type != 'shown') OR (rank_position IS NOT NULL)",
            name="ck_feedback_rank",
        ),
    )
    op.create_index(
        "ix_feedback_org_entity", "feedback_events", ["org_id", "entity_type", "entity_id"]
    )

    # ── solution_drafts ──
    op.create_table(
        "solution_drafts",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id", sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("draft_type", sa.String(30), nullable=False),
        sa.Column("requirement_profile_id", sa.String(26), nullable=True),
        sa.Column("match_run_id", sa.String(26), nullable=True),
        sa.Column("payload", JSONB(), nullable=False, server_default="{}"),
        sa.Column("engine_version", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column(
            "confirmed_by", sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("materialized_entity_id", sa.String(26), nullable=True),
        sa.Column(
            "created_by", sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index("ix_solution_drafts_org", "solution_drafts", ["org_id", "draft_type"])

    # ── creator_capability_evidence ──
    op.create_table(
        "creator_capability_evidence",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id", sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "user_id", sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("capability_key", sa.String(64), nullable=False),
        sa.Column("evidence_type", sa.String(30), nullable=False),
        sa.Column("evidence_id", sa.String(26), nullable=False),
        sa.Column("weight", sa.Numeric(3, 2), nullable=False, server_default="1.0"),
        sa.Column("score", sa.Numeric(5, 2), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index(
        "ix_evidence_user_cap", "creator_capability_evidence",
        ["org_id", "user_id", "capability_key"],
    )

    # ── creator_assignments ──
    op.create_table(
        "creator_assignments",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id", sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "project_id", sa.String(26),
            sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "user_id", sa.String(26),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("match_run_id", sa.String(26), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="offered"),
        sa.Column(
            "assigned_by", sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False,
        ),
        sa.Column("override_reason", sa.Text(), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index(
        "uq_creator_assignment", "creator_assignments", ["project_id", "user_id"], unique=True
    )

    # ── learning_path_items: workflow_pack support ──
    op.add_column(
        "learning_path_items",
        sa.Column("workflow_pack_id", sa.String(26), nullable=True),
    )
    # PG enum value addition must run outside the migration transaction
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE path_item_type ADD VALUE IF NOT EXISTS 'WORKFLOW_PACK'")
    # Extend the item-type reference constraint
    op.drop_constraint("ck_path_item_type_ref", "learning_path_items", type_="check")
    op.create_check_constraint(
        "ck_path_item_type_ref",
        "learning_path_items",
        "(item_type = 'SKILL' AND skill_id IS NOT NULL) OR "
        "(item_type = 'PROJECT' AND project_id IS NOT NULL) OR "
        "(item_type = 'SECTION' AND section_title IS NOT NULL) OR "
        "(item_type = 'WORKFLOW_PACK' AND workflow_pack_id IS NOT NULL)",
    )

    # ── skill_packs: STORED tsvector search socket (REV-6) ──
    op.execute(
        "ALTER TABLE skill_packs ADD COLUMN search_tsv tsvector "
        "GENERATED ALWAYS AS (to_tsvector('simple', "
        "coalesce(name,'') || ' ' || coalesce(summary,'') || ' ' || coalesce(description,''))) STORED"
    )
    op.execute(
        "CREATE INDEX ix_skill_packs_search_tsv ON skill_packs USING gin (search_tsv)"
    )

    # ── Seed matching configs v1 (deterministic IDs) ──
    configs = [
        (
            "01J2200000000000000CONF01",
            "workflow_pack",
            '{"capability_match": 0.35, "scenario_match": 0.20, "output_type_match": 0.20, '
            '"tool_match": 0.10, "install_popularity": 0.10, "freshness": 0.05}',
        ),
        (
            "01J2200000000000000CONF02",
            "skill_pack",
            '{"capability_teach_match": 0.35, "difficulty_fit": 0.25, "scenario_match": 0.15, '
            '"time_fit": 0.15, "popularity": 0.10}',
        ),
        (
            "01J2200000000000000CONF03",
            "project_template",
            '{"scenario_match": 0.60, "difficulty_fit": 0.40}',
        ),
        (
            "01J2200000000000000CONF04",
            "creator",
            '{"capability_evidence": 0.45, "recency": 0.20, "rubric_avg": 0.20, '
            '"commercial_history": 0.15}',
        ),
    ]
    thresholds = '{"reason_min": 0.7, "gap_max": 0.4, "tier_great": 0.75, "tier_good": 0.5}'
    for cfg_id, entity_type, weights in configs:
        op.execute(
            sa.text(
                "INSERT INTO matching_configs (id, version, target_entity_type, weights, thresholds, is_active) "
                "VALUES (:id, 1, :et, CAST(:w AS jsonb), CAST(:t AS jsonb), true)"
            ).bindparams(id=cfg_id, et=entity_type, w=weights, t=thresholds)
        )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_skill_packs_search_tsv")
    op.execute("ALTER TABLE skill_packs DROP COLUMN IF EXISTS search_tsv")
    op.drop_constraint("ck_path_item_type_ref", "learning_path_items", type_="check")
    # WORKFLOW_PACK items reference a feature this downgrade removes — their
    # rows must go BEFORE re-adding the old CHECK (whose arms don't cover the
    # type: with any such row present the ALTER TABLE fails and the whole
    # downgrade aborts mid-transaction). Their data (workflow_pack_id) is
    # dropped by the next statement anyway.
    op.execute("DELETE FROM learning_path_items WHERE item_type = 'WORKFLOW_PACK'")
    op.create_check_constraint(
        "ck_path_item_type_ref",
        "learning_path_items",
        "(item_type = 'SKILL' AND skill_id IS NOT NULL) OR "
        "(item_type = 'PROJECT' AND project_id IS NOT NULL) OR "
        "(item_type = 'SECTION' AND section_title IS NOT NULL)",
    )
    op.drop_column("learning_path_items", "workflow_pack_id")
    # Note: 'WORKFLOW_PACK' enum value cannot be removed from path_item_type in PG
    op.drop_table("creator_assignments")
    op.drop_table("creator_capability_evidence")
    op.drop_table("solution_drafts")
    op.drop_table("feedback_events")
    op.drop_table("match_results")
    op.drop_table("match_runs")
    op.drop_table("matching_configs")
    op.drop_table("requirement_profiles")
    sa.Enum(name="requirement_context").drop(op.get_bind(), checkfirst=True)
