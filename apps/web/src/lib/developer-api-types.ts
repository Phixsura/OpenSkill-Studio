/**
 * Developer Platform API Types
 * TypeScript interfaces matching backend Pydantic schemas
 */

// ── Enums ───────────────────────────────────────────

export type AppStatus = "draft" | "testing" | "submitted" | "approved" | "published" | "deprecated" | "revoked";
export type AppVisibility = "private" | "public" | "unlisted";
export type ReviewStatus = "pending" | "approved" | "rejected";
export type InstallationStatus = "active" | "suspended" | "uninstalled";
export type AppCategory = "connector" | "automation" | "analytics" | "ui_extension" | "ecosystem_source" | "content_pack" | "workflow_adapter";

// ── Developer Account ───────────────────────────────

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

export interface CreateDeveloperAccountRequest {
  display_name: string;
  slug: string;
  support_email: string;
  website_url?: string;
}

// ── App ─────────────────────────────────────────────

export interface App {
  id: string;
  developer_id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  category: AppCategory;
  visibility: AppVisibility;
  status: AppStatus;
  homepage_url: string | null;
  privacy_policy_url: string | null;
  webhook_url: string | null;
  oauth_client_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreateAppRequest {
  name: string;
  slug: string;
  category: AppCategory;
  description?: string;
  visibility?: AppVisibility;
  icon_url?: string;
  homepage_url?: string;
  webhook_url?: string;
  redirect_uris?: string[];
  manifest?: Record<string, unknown>;
}

export interface AppSummary {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon_url: string | null;
  category: AppCategory;
  visibility: AppVisibility;
  status: AppStatus;
}

// ── App Version ─────────────────────────────────────

export interface AppVersion {
  id: string;
  app_id: string;
  version: string;
  changelog: string | null;
  manifest: Record<string, unknown>;
  content_hash: string;
  review_status: ReviewStatus;
  created_at: string;
}

export interface CreateAppVersionRequest {
  version: string;
  manifest: Record<string, unknown>;
  content_hash: string;
  changelog?: string;
}

// ── Installation ────────────────────────────────────

export interface AppInstallation {
  id: string;
  app_id: string;
  app_version_id: string;
  org_id: string;
  installed_by: string;
  status: InstallationStatus;
  granted_permissions: string[];
  config: Record<string, unknown>;
  created_at: string;
}

// ── API Key ─────────────────────────────────────────

export interface ApiKey {
  id: string;
  app_id: string;
  installation_id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  rate_limit_tier: string;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface ApiKeyCreated extends ApiKey {
  raw_key: string; // Only returned once at creation
}

// ── Event Subscription ──────────────────────────────

export interface EventSubscription {
  id: string;
  installation_id: string;
  event_type: string;
  enabled: boolean;
  filter_expression: Record<string, unknown> | null;
  created_at: string;
}

// ── Automation Rule ─────────────────────────────────

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
  created_at: string;
}

// ── OAuth ───────────────────────────────────────────

export interface OAuthTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  scope: string;
}

// ── Manifest ────────────────────────────────────────

export interface Manifest {
  schema_version: string;
  app: {
    name: string;
    slug: string;
    version: string;
    category: AppCategory;
  };
  permissions: string[];
  sandbox?: {
    runtime: string;
    memory_mb: number;
    timeout_seconds: number;
    network?: {
      allowed_hosts: string[];
      egress_policy: string;
    };
  };
  event_subscriptions?: string[];
  ui_extensions?: UiExtensionDef[];
  secrets?: SecretDef[];
  config_schema?: Record<string, unknown>;
}

export interface UiExtensionDef {
  surface: string;
  title: string;
  entry: string;
  viewport?: { width: number; height: number };
}

export interface SecretDef {
  key: string;
  required?: boolean;
  description?: string;
}

// ── Health + Conformance ────────────────────────────

export interface HealthScore {
  score: number;
  status: "healthy" | "degraded" | "warning" | "critical";
  error_rate_pct: number;
  total_executions: number;
  failed_executions: number;
  timeout_executions: number;
}

export interface ConformanceCheck {
  name: string;
  status: "pass" | "fail" | "warn" | "skip";
  message: string;
  details: Record<string, unknown>;
}

export interface ConformanceReport {
  app_id: string;
  app_name: string;
  version: string;
  checked_at: string;
  checks: ConformanceCheck[];
  passed: boolean;
}

// ── API Response Wrappers ───────────────────────────

export interface DataResponse<T> {
  data: T;
}

export interface ListResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: unknown[];
  };
}
