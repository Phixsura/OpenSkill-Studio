"""eco01 ecosystem intelligence models

Revision ID: eco01a00001
Revises: talent15a00015
Create Date: 2026-09-21 21:05:46.140229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eco01a00001'
down_revision: Union[str, None] = 'talent15a00015'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('eco_ai_providers',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('canonical_name', sa.String(length=200), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('lifecycle_status', sa.String(length=20), server_default='discovered', nullable=False),
    sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('website', sa.String(length=500), nullable=True),
    sa.Column('vendor_status', sa.String(length=20), server_default='unknown', nullable=False),
    sa.Column('first_observed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_index('ix_eco_providers_lifecycle', 'eco_ai_providers', ['lifecycle_status'], unique=False)
    op.create_table('eco_external_agents',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('canonical_name', sa.String(length=200), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('lifecycle_status', sa.String(length=20), server_default='discovered', nullable=False),
    sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('agent_framework', sa.String(length=100), nullable=True),
    sa.Column('first_observed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('eco_external_workflows',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('canonical_name', sa.String(length=200), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('lifecycle_status', sa.String(length=20), server_default='discovered', nullable=False),
    sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('source_repo', sa.String(length=500), nullable=True),
    sa.Column('workflow_format', sa.String(length=20), server_default='comfyui', nullable=False),
    sa.Column('node_types', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('graph_hash', sa.String(length=64), nullable=True),
    sa.Column('first_observed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_index('ix_eco_ext_workflows_lifecycle', 'eco_external_workflows', ['lifecycle_status'], unique=False)
    op.create_table('eco_node_packages',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('canonical_name', sa.String(length=200), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('lifecycle_status', sa.String(length=20), server_default='discovered', nullable=False),
    sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('package_name', sa.String(length=200), nullable=True),
    sa.Column('repo_url', sa.String(length=500), nullable=True),
    sa.Column('latest_version', sa.String(length=100), nullable=True),
    sa.Column('security_flags', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('first_observed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('eco_ai_models',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('canonical_name', sa.String(length=200), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('lifecycle_status', sa.String(length=20), server_default='discovered', nullable=False),
    sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('provider_id', sa.String(length=26), nullable=True),
    sa.Column('modalities', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('family', sa.String(length=100), nullable=True),
    sa.Column('first_observed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['provider_id'], ['eco_ai_providers.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_index('ix_eco_models_lifecycle', 'eco_ai_models', ['lifecycle_status'], unique=False)
    op.create_index('ix_eco_models_provider', 'eco_ai_models', ['provider_id'], unique=False)
    op.create_table('eco_ai_tools',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('canonical_name', sa.String(length=200), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('lifecycle_status', sa.String(length=20), server_default='discovered', nullable=False),
    sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('provider_id', sa.String(length=26), nullable=True),
    sa.Column('tool_type', sa.String(length=20), server_default='api', nullable=False),
    sa.Column('first_observed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['provider_id'], ['eco_ai_providers.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_index('ix_eco_tools_lifecycle', 'eco_ai_tools', ['lifecycle_status'], unique=False)
    op.create_table('eco_benchmark_suites',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('key', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('family', sa.String(length=40), nullable=False),
    sa.Column('capability_key', sa.String(length=64), nullable=False),
    sa.Column('rubric', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('human_review_policy', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('automated_metrics', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('budget_usd_cap', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('repeat_count', sa.Integer(), server_default='3', nullable=False),
    sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
    sa.Column('created_by', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_index('ix_eco_bench_suites_family', 'eco_benchmark_suites', ['family', 'status'], unique=False)
    op.create_table('eco_lifecycle_transitions',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=False),
    sa.Column('entity_id', sa.String(length=26), nullable=False),
    sa.Column('from_status', sa.String(length=20), nullable=False),
    sa.Column('to_status', sa.String(length=20), nullable=False),
    sa.Column('reason', sa.String(length=40), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('actor_id', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_lifecycle_entity', 'eco_lifecycle_transitions', ['entity_kind', 'entity_id', 'created_at'], unique=False)
    op.create_table('eco_replacement_candidates',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('deprecated_kind', sa.String(length=40), nullable=False),
    sa.Column('deprecated_id', sa.String(length=26), nullable=False),
    sa.Column('candidate_kind', sa.String(length=40), nullable=False),
    sa.Column('candidate_id', sa.String(length=26), nullable=False),
    sa.Column('score', sa.Numeric(precision=5, scale=4), nullable=False),
    sa.Column('hard_compatible', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('hard_failures', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('score_breakdown', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('explanation', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('status', sa.String(length=20), server_default='proposed', nullable=False),
    sa.Column('decided_by', sa.String(length=26), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['decided_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_candidates_deprecated', 'eco_replacement_candidates', ['deprecated_kind', 'deprecated_id', 'status'], unique=False)
    op.create_table('eco_replacement_edges',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('from_kind', sa.String(length=40), nullable=False),
    sa.Column('from_id', sa.String(length=26), nullable=False),
    sa.Column('to_kind', sa.String(length=40), nullable=False),
    sa.Column('to_id', sa.String(length=26), nullable=False),
    sa.Column('edge_type', sa.String(length=40), nullable=False),
    sa.Column('rationale', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('from_kind', 'from_id', 'to_kind', 'to_id', 'edge_type', name='uq_eco_repl_edge')
    )
    op.create_index('ix_eco_repl_from', 'eco_replacement_edges', ['from_kind', 'from_id'], unique=False)
    op.create_table('eco_sources',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('source_type', sa.String(length=40), nullable=False),
    sa.Column('trust_level', sa.String(length=20), nullable=False),
    sa.Column('base_url', sa.String(length=2000), nullable=True),
    sa.Column('adapter_key', sa.String(length=64), nullable=False),
    sa.Column('parser_version', sa.String(length=20), nullable=False),
    sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('sync_interval_minutes', sa.Integer(), server_default='1440', nullable=False),
    sa.Column('rate_limit_per_hour', sa.Integer(), server_default='60', nullable=False),
    sa.Column('max_response_bytes', sa.Integer(), server_default='5242880', nullable=False),
    sa.Column('timeout_seconds', sa.Integer(), server_default='30', nullable=False),
    sa.Column('etag', sa.String(length=500), nullable=True),
    sa.Column('last_modified', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=20), server_default='active', nullable=False),
    sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('consecutive_failures', sa.Integer(), server_default='0', nullable=False),
    sa.Column('robots_compliant', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_by', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index('ix_eco_sources_status', 'eco_sources', ['status'], unique=False)
    op.create_index('ix_eco_sources_type', 'eco_sources', ['source_type'], unique=False)
    op.create_table('eco_benchmark_cases',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('suite_id', sa.String(length=26), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('prompt', sa.Text(), nullable=False),
    sa.Column('reference_assets', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('constraints', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('weight', sa.Numeric(precision=4, scale=3), nullable=False),
    sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['suite_id'], ['eco_benchmark_suites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_bench_cases_suite', 'eco_benchmark_cases', ['suite_id', 'sort_order'], unique=False)
    op.create_table('eco_benchmark_runs',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('suite_id', sa.String(length=26), nullable=False),
    sa.Column('status', sa.String(length=20), server_default='queued', nullable=False),
    sa.Column('target', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('environment_snapshot', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('seed_settings', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('budget_usd_cap', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('total_cost_usd', sa.Numeric(precision=12, scale=6), nullable=False),
    sa.Column('dimension_scores', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('triggered_by', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['suite_id'], ['eco_benchmark_suites.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['triggered_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_bench_runs_status', 'eco_benchmark_runs', ['status'], unique=False)
    op.create_index('ix_eco_bench_runs_suite', 'eco_benchmark_runs', ['suite_id', 'created_at'], unique=False)
    op.create_table('eco_entity_aliases',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=False),
    sa.Column('entity_id', sa.String(length=26), nullable=False),
    sa.Column('alias', sa.String(length=300), nullable=False),
    sa.Column('alias_type', sa.String(length=30), server_default='name', nullable=False),
    sa.Column('source_id', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['eco_sources.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('entity_kind', 'alias', 'alias_type', name='uq_eco_alias')
    )
    op.create_index('ix_eco_aliases_entity', 'eco_entity_aliases', ['entity_kind', 'entity_id'], unique=False)
    op.create_table('eco_model_versions',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('model_id', sa.String(length=26), nullable=False),
    sa.Column('version', sa.String(length=100), nullable=False),
    sa.Column('canonical_name', sa.String(length=200), nullable=False),
    sa.Column('lifecycle_status', sa.String(length=20), server_default='discovered', nullable=False),
    sa.Column('external_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('released_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deprecated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('sunset_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('api_identifier', sa.String(length=200), nullable=True),
    sa.Column('limits', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('license', sa.String(length=100), nullable=True),
    sa.Column('commercial_use_allowed', sa.Boolean(), nullable=True),
    sa.Column('first_observed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['model_id'], ['eco_ai_models.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('model_id', 'version', name='uq_eco_model_version')
    )
    op.create_index('ix_eco_model_versions_lifecycle', 'eco_model_versions', ['lifecycle_status'], unique=False)
    op.create_index('ix_eco_model_versions_sunset', 'eco_model_versions', ['sunset_at'], unique=False)
    op.create_table('eco_review_batches',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('suite_id', sa.String(length=26), nullable=False),
    sa.Column('run_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('alias_map', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('reviewer_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('blind', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('status', sa.String(length=20), server_default='open', nullable=False),
    sa.Column('created_by', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['suite_id'], ['eco_benchmark_suites.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_review_batches_suite', 'eco_review_batches', ['suite_id'], unique=False)
    op.create_table('eco_rollout_plans',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('replacement_candidate_id', sa.String(length=26), nullable=False),
    sa.Column('scope_type', sa.String(length=30), nullable=False),
    sa.Column('scope_ref', sa.String(length=26), nullable=True),
    sa.Column('baseline', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('candidate_metrics', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('comparison', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
    sa.Column('decided_by', sa.String(length=26), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['decided_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['replacement_candidate_id'], ['eco_replacement_candidates.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_rollouts_status', 'eco_rollout_plans', ['status'], unique=False)
    op.create_table('eco_source_sync_runs',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('source_id', sa.String(length=26), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=20), server_default='running', nullable=False),
    sa.Column('http_status', sa.Integer(), nullable=True),
    sa.Column('bytes_fetched', sa.Integer(), server_default='0', nullable=False),
    sa.Column('observations_created', sa.Integer(), server_default='0', nullable=False),
    sa.Column('changes_detected', sa.Integer(), server_default='0', nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('parser_version', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['eco_sources.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_sync_runs_source', 'eco_source_sync_runs', ['source_id', 'started_at'], unique=False)
    op.create_table('eco_benchmark_results',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('run_id', sa.String(length=26), nullable=False),
    sa.Column('case_id', sa.String(length=26), nullable=False),
    sa.Column('repeat_index', sa.Integer(), nullable=False),
    sa.Column('input_snapshot', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('output_assets', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('latency_ms', sa.Integer(), nullable=True),
    sa.Column('usage', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('cost_usd', sa.Numeric(precision=12, scale=6), nullable=False),
    sa.Column('retries', sa.Integer(), server_default='0', nullable=False),
    sa.Column('failed', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('automated_scores', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['case_id'], ['eco_benchmark_cases.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['run_id'], ['eco_benchmark_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('run_id', 'case_id', 'repeat_index', name='uq_eco_bench_result')
    )
    op.create_index('ix_eco_bench_results_run', 'eco_benchmark_results', ['run_id'], unique=False)
    op.create_table('eco_component_drafts',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('draft_type', sa.String(length=40), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('source_kind', sa.String(length=40), nullable=True),
    sa.Column('source_id', sa.String(length=26), nullable=True),
    sa.Column('source_observation_ids', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('validation', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
    sa.Column('org_id', sa.String(length=26), nullable=True),
    sa.Column('created_by', sa.String(length=26), nullable=True),
    sa.Column('reviewed_by', sa.String(length=26), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('published_ref', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_drafts_status', 'eco_component_drafts', ['draft_type', 'status'], unique=False)
    op.create_table('eco_dependency_edges',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('from_kind', sa.String(length=40), nullable=False),
    sa.Column('from_id', sa.String(length=26), nullable=False),
    sa.Column('to_kind', sa.String(length=40), nullable=False),
    sa.Column('to_id', sa.String(length=26), nullable=False),
    sa.Column('constraint_type', sa.String(length=40), server_default='uses', nullable=False),
    sa.Column('constraint_spec', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('org_id', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('from_kind', 'from_id', 'to_kind', 'to_id', 'constraint_type', name='uq_eco_dep_edge')
    )
    op.create_index('ix_eco_dep_from', 'eco_dependency_edges', ['from_kind', 'from_id'], unique=False)
    op.create_index('ix_eco_dep_to', 'eco_dependency_edges', ['to_kind', 'to_id'], unique=False)
    op.create_table('eco_observations',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('source_id', sa.String(length=26), nullable=False),
    sa.Column('sync_run_id', sa.String(length=26), nullable=True),
    sa.Column('event_type', sa.String(length=40), nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=True),
    sa.Column('external_ref', sa.String(length=500), nullable=True),
    sa.Column('canonical_entity_id', sa.String(length=26), nullable=True),
    sa.Column('canonical_entity_kind', sa.String(length=30), nullable=True),
    sa.Column('observed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('effective_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('raw_hash', sa.String(length=64), nullable=False),
    sa.Column('normalized', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('parser_version', sa.String(length=20), nullable=False),
    sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
    sa.Column('provenance_url', sa.String(length=2000), nullable=True),
    sa.Column('extraction_method', sa.String(length=20), server_default='structured', nullable=False),
    sa.Column('human_verified', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('verified_by', sa.String(length=26), nullable=True),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('superseded_by_id', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['eco_sources.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['superseded_by_id'], ['eco_observations.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['sync_run_id'], ['eco_source_sync_runs.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('source_id', 'raw_hash', 'event_type', name='uq_eco_obs_idem')
    )
    op.create_index('ix_eco_obs_entity', 'eco_observations', ['canonical_entity_kind', 'canonical_entity_id'], unique=False)
    op.create_index('ix_eco_obs_event', 'eco_observations', ['event_type', 'observed_at'], unique=False)
    op.create_index('ix_eco_obs_external_ref', 'eco_observations', ['external_ref'], unique=False)
    op.create_table('eco_telemetry_snapshots',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=False),
    sa.Column('entity_id', sa.String(length=26), nullable=False),
    sa.Column('window_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('window_end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('org_id', sa.String(length=26), nullable=True),
    sa.Column('sample_size', sa.Integer(), nullable=False),
    sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('entity_kind', 'entity_id', 'org_id', 'window_start', 'window_end', name='uq_eco_telemetry_window')
    )
    op.create_index('ix_eco_telemetry_entity', 'eco_telemetry_snapshots', ['entity_kind', 'entity_id', 'window_end'], unique=False)
    op.create_table('eco_watchlists',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('owner_id', sa.String(length=26), nullable=False),
    sa.Column('org_id', sa.String(length=26), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_watchlists_owner', 'eco_watchlists', ['owner_id'], unique=False)
    op.create_table('eco_availability_records',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=False),
    sa.Column('entity_id', sa.String(length=26), nullable=False),
    sa.Column('region', sa.String(length=30), nullable=True),
    sa.Column('record_type', sa.String(length=20), nullable=False),
    sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('observed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('source_observation_id', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['source_observation_id'], ['eco_observations.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_avail_entity', 'eco_availability_records', ['entity_kind', 'entity_id', 'record_type', 'observed_at'], unique=False)
    op.create_table('eco_benchmark_reviews',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('batch_id', sa.String(length=26), nullable=False),
    sa.Column('run_id', sa.String(length=26), nullable=False),
    sa.Column('result_id', sa.String(length=26), nullable=False),
    sa.Column('reviewer_id', sa.String(length=26), nullable=False),
    sa.Column('alias_label', sa.String(length=8), nullable=False),
    sa.Column('scores', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['batch_id'], ['eco_review_batches.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['result_id'], ['eco_benchmark_results.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['run_id'], ['eco_benchmark_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('result_id', 'reviewer_id', name='uq_eco_bench_review')
    )
    op.create_index('ix_eco_bench_reviews_batch', 'eco_benchmark_reviews', ['batch_id'], unique=False)
    op.create_table('eco_capability_mappings',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=False),
    sa.Column('entity_id', sa.String(length=26), nullable=False),
    sa.Column('capability_key', sa.String(length=64), nullable=False),
    sa.Column('evidence_level', sa.String(length=30), server_default='vendor_claimed', nullable=False),
    sa.Column('io_spec', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
    sa.Column('source_observation_id', sa.String(length=26), nullable=True),
    sa.Column('verified_by', sa.String(length=26), nullable=True),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['source_observation_id'], ['eco_observations.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('entity_kind', 'entity_id', 'capability_key', name='uq_eco_cap_mapping')
    )
    op.create_index('ix_eco_cap_mapping_entity', 'eco_capability_mappings', ['entity_kind', 'entity_id'], unique=False)
    op.create_index('ix_eco_cap_mapping_key', 'eco_capability_mappings', ['capability_key'], unique=False)
    op.create_table('eco_change_events',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('observation_id', sa.String(length=26), nullable=False),
    sa.Column('change_type', sa.String(length=30), nullable=False),
    sa.Column('field', sa.String(length=100), nullable=False),
    sa.Column('old_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('new_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('severity', sa.String(length=30), server_default='info', nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=True),
    sa.Column('canonical_entity_id', sa.String(length=26), nullable=True),
    sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('acknowledged', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('acknowledged_by', sa.String(length=26), nullable=True),
    sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['observation_id'], ['eco_observations.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_changes_entity', 'eco_change_events', ['entity_kind', 'canonical_entity_id'], unique=False)
    op.create_index('ix_eco_changes_severity', 'eco_change_events', ['severity', 'acknowledged'], unique=False)
    op.create_index('ix_eco_changes_type', 'eco_change_events', ['change_type', 'detected_at'], unique=False)
    op.create_table('eco_price_observations',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('observation_id', sa.String(length=26), nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=False),
    sa.Column('entity_id', sa.String(length=26), nullable=False),
    sa.Column('region', sa.String(length=30), nullable=True),
    sa.Column('unit', sa.String(length=30), nullable=False),
    sa.Column('price', sa.Numeric(precision=14, scale=6), nullable=False),
    sa.Column('currency', sa.String(length=3), server_default='USD', nullable=False),
    sa.Column('tier', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('effective_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('observed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('reconciliation_status', sa.String(length=20), server_default='unreviewed', nullable=False),
    sa.Column('reconciled_by', sa.String(length=26), nullable=True),
    sa.Column('reconciled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('approved_cost_rate_id', sa.String(length=26), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['observation_id'], ['eco_observations.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['reconciled_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_price_obs_entity', 'eco_price_observations', ['entity_kind', 'entity_id', 'observed_at'], unique=False)
    op.create_index('ix_eco_price_obs_status', 'eco_price_observations', ['reconciliation_status'], unique=False)
    op.create_table('eco_resolution_candidates',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('observation_id', sa.String(length=26), nullable=False),
    sa.Column('entity_kind', sa.String(length=30), nullable=False),
    sa.Column('candidate_entity_id', sa.String(length=26), nullable=True),
    sa.Column('match_method', sa.String(length=20), nullable=False),
    sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=False),
    sa.Column('proposed_payload', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
    sa.Column('decided_by', sa.String(length=26), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['decided_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['observation_id'], ['eco_observations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_resolution_obs', 'eco_resolution_candidates', ['observation_id'], unique=False)
    op.create_index('ix_eco_resolution_status', 'eco_resolution_candidates', ['status'], unique=False)
    op.create_table('eco_watch_items',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('watchlist_id', sa.String(length=26), nullable=False),
    sa.Column('target_kind', sa.String(length=30), nullable=False),
    sa.Column('target_id', sa.String(length=26), nullable=True),
    sa.Column('target_ref', sa.String(length=300), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['watchlist_id'], ['eco_watchlists.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_watch_items_list', 'eco_watch_items', ['watchlist_id'], unique=False)
    op.create_table('eco_impact_analyses',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('change_event_id', sa.String(length=26), nullable=False),
    sa.Column('root_kind', sa.String(length=40), nullable=False),
    sa.Column('root_id', sa.String(length=26), nullable=False),
    sa.Column('classification', sa.String(length=30), nullable=False),
    sa.Column('summary', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('deadline_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('status', sa.String(length=20), server_default='open', nullable=False),
    sa.ForeignKeyConstraint(['change_event_id'], ['eco_change_events.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_impact_root', 'eco_impact_analyses', ['root_kind', 'root_id'], unique=False)
    op.create_index('ix_eco_impact_status', 'eco_impact_analyses', ['status', 'classification'], unique=False)
    op.create_table('eco_impact_items',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('analysis_id', sa.String(length=26), nullable=False),
    sa.Column('node_kind', sa.String(length=40), nullable=False),
    sa.Column('node_id', sa.String(length=26), nullable=False),
    sa.Column('depth', sa.Integer(), nullable=False),
    sa.Column('path', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('active_usage', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('recommended_action', sa.String(length=40), server_default='review', nullable=False),
    sa.ForeignKeyConstraint(['analysis_id'], ['eco_impact_analyses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eco_impact_items_analysis', 'eco_impact_items', ['analysis_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_eco_impact_items_analysis', table_name='eco_impact_items')
    op.drop_table('eco_impact_items')
    op.drop_index('ix_eco_impact_status', table_name='eco_impact_analyses')
    op.drop_index('ix_eco_impact_root', table_name='eco_impact_analyses')
    op.drop_table('eco_impact_analyses')
    op.drop_index('ix_eco_watch_items_list', table_name='eco_watch_items')
    op.drop_table('eco_watch_items')
    op.drop_index('ix_eco_resolution_status', table_name='eco_resolution_candidates')
    op.drop_index('ix_eco_resolution_obs', table_name='eco_resolution_candidates')
    op.drop_table('eco_resolution_candidates')
    op.drop_index('ix_eco_price_obs_status', table_name='eco_price_observations')
    op.drop_index('ix_eco_price_obs_entity', table_name='eco_price_observations')
    op.drop_table('eco_price_observations')
    op.drop_index('ix_eco_changes_type', table_name='eco_change_events')
    op.drop_index('ix_eco_changes_severity', table_name='eco_change_events')
    op.drop_index('ix_eco_changes_entity', table_name='eco_change_events')
    op.drop_table('eco_change_events')
    op.drop_index('ix_eco_cap_mapping_key', table_name='eco_capability_mappings')
    op.drop_index('ix_eco_cap_mapping_entity', table_name='eco_capability_mappings')
    op.drop_table('eco_capability_mappings')
    op.drop_index('ix_eco_bench_reviews_batch', table_name='eco_benchmark_reviews')
    op.drop_table('eco_benchmark_reviews')
    op.drop_index('ix_eco_avail_entity', table_name='eco_availability_records')
    op.drop_table('eco_availability_records')
    op.drop_index('ix_eco_watchlists_owner', table_name='eco_watchlists')
    op.drop_table('eco_watchlists')
    op.drop_index('ix_eco_telemetry_entity', table_name='eco_telemetry_snapshots')
    op.drop_table('eco_telemetry_snapshots')
    op.drop_index('ix_eco_obs_external_ref', table_name='eco_observations')
    op.drop_index('ix_eco_obs_event', table_name='eco_observations')
    op.drop_index('ix_eco_obs_entity', table_name='eco_observations')
    op.drop_table('eco_observations')
    op.drop_index('ix_eco_dep_to', table_name='eco_dependency_edges')
    op.drop_index('ix_eco_dep_from', table_name='eco_dependency_edges')
    op.drop_table('eco_dependency_edges')
    op.drop_index('ix_eco_drafts_status', table_name='eco_component_drafts')
    op.drop_table('eco_component_drafts')
    op.drop_index('ix_eco_bench_results_run', table_name='eco_benchmark_results')
    op.drop_table('eco_benchmark_results')
    op.drop_index('ix_eco_sync_runs_source', table_name='eco_source_sync_runs')
    op.drop_table('eco_source_sync_runs')
    op.drop_index('ix_eco_rollouts_status', table_name='eco_rollout_plans')
    op.drop_table('eco_rollout_plans')
    op.drop_index('ix_eco_review_batches_suite', table_name='eco_review_batches')
    op.drop_table('eco_review_batches')
    op.drop_index('ix_eco_model_versions_sunset', table_name='eco_model_versions')
    op.drop_index('ix_eco_model_versions_lifecycle', table_name='eco_model_versions')
    op.drop_table('eco_model_versions')
    op.drop_index('ix_eco_aliases_entity', table_name='eco_entity_aliases')
    op.drop_table('eco_entity_aliases')
    op.drop_index('ix_eco_bench_runs_suite', table_name='eco_benchmark_runs')
    op.drop_index('ix_eco_bench_runs_status', table_name='eco_benchmark_runs')
    op.drop_table('eco_benchmark_runs')
    op.drop_index('ix_eco_bench_cases_suite', table_name='eco_benchmark_cases')
    op.drop_table('eco_benchmark_cases')
    op.drop_index('ix_eco_sources_type', table_name='eco_sources')
    op.drop_index('ix_eco_sources_status', table_name='eco_sources')
    op.drop_table('eco_sources')
    op.drop_index('ix_eco_repl_from', table_name='eco_replacement_edges')
    op.drop_table('eco_replacement_edges')
    op.drop_index('ix_eco_candidates_deprecated', table_name='eco_replacement_candidates')
    op.drop_table('eco_replacement_candidates')
    op.drop_index('ix_eco_lifecycle_entity', table_name='eco_lifecycle_transitions')
    op.drop_table('eco_lifecycle_transitions')
    op.drop_index('ix_eco_bench_suites_family', table_name='eco_benchmark_suites')
    op.drop_table('eco_benchmark_suites')
    op.drop_index('ix_eco_tools_lifecycle', table_name='eco_ai_tools')
    op.drop_table('eco_ai_tools')
    op.drop_index('ix_eco_models_provider', table_name='eco_ai_models')
    op.drop_index('ix_eco_models_lifecycle', table_name='eco_ai_models')
    op.drop_table('eco_ai_models')
    op.drop_table('eco_node_packages')
    op.drop_index('ix_eco_ext_workflows_lifecycle', table_name='eco_external_workflows')
    op.drop_table('eco_external_workflows')
    op.drop_table('eco_external_agents')
    op.drop_index('ix_eco_providers_lifecycle', table_name='eco_ai_providers')
    op.drop_table('eco_ai_providers')
    # ### end Alembic commands ###

