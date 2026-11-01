/**
 * Core type definitions for the OpenSkill Platform SDK.
 */

// ── Enums ────────────────────────────────────────────────

export type AppCategory =
  | "connector"
  | "workflow_adapter"
  | "ui_extension"
  | "analytics"
  | "automation"
  | "content_pack"
  | "ecosystem_source";

export type AppStatus =
  | "draft"
  | "testing"
  | "submitted"
  | "approved"
  | "published"
  | "deprecated"
  | "revoked";

export type AppVisibility = "private" | "unlisted" | "public";

export type ReviewStatus = "pending" | "approved" | "rejected" | "revoked";

export type InstallationStatus = "active" | "suspended" | "uninstalled";

export type Permission =
  | "read:organizations"
  | "write:organizations"
  | "read:members"
  | "write:members"
  | "read:cohorts"
  | "write:cohorts"
  | "read:cohort_members"
  | "read:projects"
  | "write:projects"
  | "read:submissions"
  | "write:project_results"
  | "read:skills"
  | "write:skills"
  | "read:skill_progress"
  | "read:packs"
  | "write:packs"
  | "read:installations"
  | "read:workflows"
  | "write:workflows"
  | "read:workflow_runs"
  | "write:workflow_runs"
  | "read:providers"
  | "write:providers"
  | "read:credentials"
  | "read:talent"
  | "write:talent"
  | "read:passports"
  | "read:opportunities"
  | "read:evaluations"
  | "write:evaluations"
  | "read:matching"
  | "write:matching"
  | "read:marketplace"
  | "write:marketplace_listings"
  | "subscribe:events"
  | "extend:ui"
  | "read:analytics"
  | "export:analytics"
  | "read:settings"
  | "write:settings"
  | "read:users"
  | "read:user_profiles"
  | "run:background_jobs";

// ── Entity types ────────────────────────────────────────

export interface DeveloperAccount {
  id: string;
  owner_user_id: string;
  org_id: string | null;
  display_name: string;
  slug: string;
  website_url: string | null;
  support_email: string;
  verified: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface App {
  id: string;
  developer_id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  homepage_url: string | null;
  privacy_policy_url: string | null;
  category: AppCategory;
  visibility: AppVisibility;
  status: AppStatus;
  manifest: Manifest | null;
  oauth_client_id: string | null;
  redirect_uris: string[] | null;
  webhook_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppVersion {
  id: string;
  app_id: string;
  version: string;
  changelog: string | null;
  content_hash: string;
  signature: string | null;
  review_status: ReviewStatus;
  review_notes: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  min_platform_version: string | null;
  created_at: string;
}

export interface AppInstallation {
  id: string;
  app_id: string;
  app_version_id: string;
  org_id: string;
  tenant_id: string | null;
  installed_by: string;
  status: InstallationStatus;
  granted_permissions: Permission[];
  config: Record<string, unknown>;
  pinned_version: boolean;
  created_at: string;
  updated_at: string;
  uninstalled_at: string | null;
}

export interface ApiKey {
  id: string;
  app_id: string;
  installation_id: string | null;
  name: string;
  key_prefix: string;
  scopes: string[];
  rate_limit_tier: string;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface EventSubscription {
  id: string;
  installation_id: string;
  event_type: string;
  enabled: boolean;
  filter_expression: Record<string, unknown> | null;
  created_at: string;
}

export interface AutomationRule {
  id: string;
  installation_id: string;
  name: string;
  trigger_event: string;
  trigger_filter: Record<string, unknown> | null;
  action_type: string;
  action_config: Record<string, unknown>;
  enabled: boolean;
  max_executions_per_hour: number;
  last_executed_at: string | null;
  execution_count: number;
  created_at: string;
  updated_at: string;
}

// ── Manifest ────────────────────────────────────────────

export interface Manifest {
  schema_version: string;
  app: {
    name: string;
    slug?: string;
    version?: string;
    category?: AppCategory;
    min_platform_version?: string;
  };
  permissions: Permission[];
  scopes?: {
    data?: string[];
    events?: string[];
    ui?: string[];
    capabilities?: string[];
  };
  oauth?: {
    redirect_uris: string[];
    token_endpoint_auth_method?: string;
  };
  sandbox?: {
    runtime?: string;
    memory_mb?: number;
    timeout_seconds?: number;
    network?: {
      allowed_hosts?: string[];
      egress_policy?: "allowlist" | "deny_all";
    };
  };
  ui_extensions?: UiExtensionConfig[];
  event_subscriptions?: string[];
  secrets?: SecretConfig[];
  config_schema?: Record<string, unknown>;
}

export interface UiExtensionConfig {
  surface: string;
  title: string;
  entry: string;
  viewport?: { width?: number; height?: number };
}

export interface SecretConfig {
  key: string;
  description?: string;
  required?: boolean;
}

// ── API response wrappers ───────────────────────────────

export interface DataResponse<T> {
  data: T;
}

export interface ListResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

export interface PaginationMeta {
  total: number;
  page: number;
  per_page: number;
  has_more: boolean;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: unknown[];
  };
}
