"""Capability taxonomy + provider four-entity model (Issue #21, ADR-011)

Revision ID: f7a81c223001
Revises: e6f70b112100
Create Date: 2026-08-23 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "f7a81c223001"
down_revision: str | None = "e6f70b112100"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── capability_tags ──
    op.create_table(
        "capability_tags",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("key", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("category", sa.String(30), nullable=False, server_default="generation"),
        sa.Column("contract_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("io_signature", JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_platform", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_capability_category", "capability_tags", ["category"])

    # ── provider_adapters ──
    op.create_table(
        "provider_adapters",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("key", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("config_schema", JSONB(), nullable=False, server_default="{}"),
        sa.Column("credential_fields", JSONB(), nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ── org_credentials ──
    op.create_table(
        "org_credentials",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("encrypted_data", sa.Text(), nullable=False),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_org_credentials_org", "org_credentials", ["org_id"])

    # ── provider_connections ──
    op.create_table(
        "provider_connections",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "org_id",
            sa.String(26),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "adapter_id",
            sa.String(26),
            sa.ForeignKey("provider_adapters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("config", JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "credential_id",
            sa.String(26),
            sa.ForeignKey("org_credentials.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("last_health_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("health_status", sa.String(20), nullable=True),
        sa.Column(
            "created_by",
            sa.String(26),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_provider_conn_org", "provider_connections", ["org_id"])

    # ── provider_model_offerings ──
    op.create_table(
        "provider_model_offerings",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column(
            "connection_id",
            sa.String(26),
            sa.ForeignKey("provider_connections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("capability_key", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(200), nullable=False),
        sa.Column("features", JSONB(), nullable=False, server_default="[]"),
        sa.Column("limits", JSONB(), nullable=False, server_default="{}"),
        sa.Column("cost_per_call_usd", sa.Numeric(10, 6), nullable=True),
        sa.Column("quality_tier", sa.String(20), nullable=False, server_default="standard"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_offering_capability", "provider_model_offerings", ["capability_key"])
    op.create_index("ix_offering_connection", "provider_model_offerings", ["connection_id"])

    # ── Seed platform capabilities (deterministic IDs — consistent across envs) ──
    capabilities = [
        # (id, key, name, category, io_signature)
        ("01J21000000000000000IMGGEN", "image_generation", "Image Generation", "generation",
         '{"inputs": ["prompt"], "outputs": ["image"]}'),
        ("01J21000000000000000IMGEDT", "image_editing", "Image Editing", "editing",
         '{"inputs": ["image", "prompt"], "outputs": ["image"]}'),
        ("01J21000000000000000IMG2VD", "image_to_video", "Image to Video", "generation",
         '{"inputs": ["image", "prompt"], "outputs": ["video"]}'),
        ("01J21000000000000000TXT2VD", "text_to_video", "Text to Video", "generation",
         '{"inputs": ["prompt"], "outputs": ["video"]}'),
        ("01J21000000000000000VIDEDT", "video_editing", "Video Editing", "editing",
         '{"inputs": ["video"], "outputs": ["video"]}'),
        ("01J21000000000000000VOICEG", "voice_generation", "Voice Generation", "audio",
         '{"inputs": ["text"], "outputs": ["audio"]}'),
        ("01J21000000000000000MMRVW0", "multimodal_review", "Multimodal Review", "review",
         '{"inputs": ["image", "prompt"], "outputs": ["json"]}'),
        ("01J21000000000000000UPSCAL", "upscale", "Upscale", "editing",
         '{"inputs": ["image"], "outputs": ["image"]}'),
        ("01J21000000000000000BGREMV", "background_removal", "Background Removal", "editing",
         '{"inputs": ["image"], "outputs": ["image"]}'),
    ]
    for cap_id, key, name, category, io_sig in capabilities:
        op.execute(
            sa.text(
                "INSERT INTO capability_tags (id, key, name, category, io_signature) "
                "VALUES (:id, :key, :name, :category, CAST(:io_sig AS jsonb))"
            ).bindparams(id=cap_id, key=key, name=name, category=category, io_sig=io_sig)
        )

    # ── Seed platform adapters ──
    adapters = [
        # (id, key, name, description, config_schema, credential_fields)
        ("01J21000000000000000MOCK00", "mock", "Mock Provider",
         "Deterministic echo adapter for testing and demos", "{}", "[]"),
        ("01J21000000000000000ANTHRO", "anthropic", "Anthropic",
         "Claude multimodal review adapter", "{}", '["api_key"]'),
    ]
    for a_id, key, name, desc, cfg, creds in adapters:
        op.execute(
            sa.text(
                "INSERT INTO provider_adapters (id, key, name, description, config_schema, credential_fields) "
                "VALUES (:id, :key, :name, :descr, CAST(:cfg AS jsonb), CAST(:creds AS jsonb))"
            ).bindparams(id=a_id, key=key, name=name, descr=desc, cfg=cfg, creds=creds)
        )


def downgrade() -> None:
    op.drop_index("ix_offering_connection", table_name="provider_model_offerings")
    op.drop_index("ix_offering_capability", table_name="provider_model_offerings")
    op.drop_table("provider_model_offerings")
    op.drop_index("ix_provider_conn_org", table_name="provider_connections")
    op.drop_table("provider_connections")
    op.drop_index("ix_org_credentials_org", table_name="org_credentials")
    op.drop_table("org_credentials")
    op.drop_table("provider_adapters")
    op.drop_index("ix_capability_category", table_name="capability_tags")
    op.drop_table("capability_tags")
