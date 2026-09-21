"""eco03: pg_trgm-backed entity resolution (deps.dev/HF-grade, ADR-016 §11 follow-up).

- pg_trgm extension
- eco_entity_aliases.alias_normalized (casefolded, punctuation-stripped) + GIN
  trigram index — deterministic lookups hit the normalized key, similarity
  candidates come from an indexed trigram scan instead of a Python full scan.
- GIN trigram indexes on canonical_name for all seven catalog tables.
"""

import sqlalchemy as sa
from alembic import op

revision: str = "eco03a00003"
down_revision: str = "eco02a00002"
branch_labels = None
depends_on = None

_CATALOG_TABLES = [
    "eco_ai_providers",
    "eco_ai_tools",
    "eco_ai_models",
    "eco_model_versions",
    "eco_external_workflows",
    "eco_external_agents",
    "eco_node_packages",
]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.add_column(
        "eco_entity_aliases",
        sa.Column("alias_normalized", sa.String(300), nullable=True),
    )
    # Backfill: same normalization the service applies (lower + squash non-alnum)
    op.execute(
        "UPDATE eco_entity_aliases SET alias_normalized = "
        "trim(both ' ' from regexp_replace(lower(alias), '[^a-z0-9]+', ' ', 'g'))"
    )
    op.create_index(
        "ix_eco_aliases_normalized",
        "eco_entity_aliases",
        ["entity_kind", "alias_normalized"],
    )
    op.execute(
        "CREATE INDEX ix_eco_aliases_trgm ON eco_entity_aliases "
        "USING gin (alias_normalized gin_trgm_ops)"
    )
    for table in _CATALOG_TABLES:
        op.execute(
            f"CREATE INDEX ix_{table}_name_trgm ON {table} "
            f"USING gin (lower(canonical_name) gin_trgm_ops)"
        )


def downgrade() -> None:
    for table in _CATALOG_TABLES:
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_eco_aliases_trgm")
    op.drop_index("ix_eco_aliases_normalized", table_name="eco_entity_aliases")
    op.drop_column("eco_entity_aliases", "alias_normalized")
