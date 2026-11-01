/**
 * OpenSkill Platform API client.
 */

import { ApiError, AuthError, NotFoundError, RateLimitError } from "./errors.js";
import type {
  App,
  AppInstallation,
  AppVersion,
  ApiKey,
  AutomationRule,
  DataResponse,
  DeveloperAccount,
  EventSubscription,
  ListResponse,
  PaginationMeta,
} from "./types.js";

export interface ClientConfig {
  /** API key (osk_app_...) or OAuth access token */
  apiKey: string;
  /** Base URL of the OpenSkill API (default: https://api.openskill.dev) */
  baseUrl?: string;
  /** Request timeout in ms (default: 30000) */
  timeout?: number;
  /** Custom fetch implementation (for testing or Node 16) */
  fetch?: typeof globalThis.fetch;
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  headers?: Record<string, string>;
}

export class OpenSkillClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly timeout: number;
  private readonly _fetch: typeof globalThis.fetch;

  /** Developer account operations */
  readonly developer: DeveloperResource;
  /** App management */
  readonly apps: AppResource;
  /** Cohort operations (scoped to installation permissions) */
  readonly cohorts: CrudResource<unknown>;
  /** Project operations */
  readonly projects: CrudResource<unknown>;
  /** Marketplace browsing */
  readonly marketplace: MarketplaceResource;

  constructor(config: ClientConfig) {
    this.baseUrl = (config.baseUrl ?? "https://api.openskill.dev").replace(
      /\/$/,
      "",
    );
    this.apiKey = config.apiKey;
    this.timeout = config.timeout ?? 30_000;
    this._fetch = config.fetch ?? globalThis.fetch.bind(globalThis);

    this.developer = new DeveloperResource(this);
    this.apps = new AppResource(this);
    this.cohorts = new CrudResource(this, "cohorts");
    this.projects = new CrudResource(this, "projects");
    this.marketplace = new MarketplaceResource(this);
  }

  /** Make an authenticated API request */
  async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const url = new URL(`/api/v1${path}`, this.baseUrl);
    if (options.query) {
      for (const [k, v] of Object.entries(options.query)) {
        if (v !== undefined) url.searchParams.set(k, String(v));
      }
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const res = await this._fetch(url.toString(), {
        method: options.method ?? "GET",
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          "Content-Type": "application/json",
          ...options.headers,
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        const error = (body as { error?: { code?: string; message?: string } })
          .error;

        if (res.status === 401) throw new AuthError(error?.message);
        if (res.status === 404) throw new NotFoundError(error?.message);
        if (res.status === 429) {
          const retryAfter = parseInt(
            res.headers.get("retry-after") ?? "60",
            10,
          );
          throw new RateLimitError(retryAfter, error?.message);
        }
        throw new ApiError(
          error?.message ?? `HTTP ${res.status}`,
          error?.code ?? "API_ERROR",
          res.status,
        );
      }

      return (await res.json()) as T;
    } finally {
      clearTimeout(timer);
    }
  }
}

// ── Resource classes ────────────────────────────────────

class DeveloperResource {
  constructor(private client: OpenSkillClient) {}

  /** Get the current user's developer account */
  async getMe(): Promise<DeveloperAccount> {
    const res = await this.client.request<DataResponse<DeveloperAccount>>(
      "/developer/accounts/me",
    );
    return res.data;
  }

  /** Create a developer account */
  async create(data: {
    display_name: string;
    slug: string;
    support_email: string;
    website_url?: string;
    org_id?: string;
  }): Promise<DeveloperAccount> {
    const res = await this.client.request<DataResponse<DeveloperAccount>>(
      "/developer/accounts",
      { method: "POST", body: data },
    );
    return res.data;
  }
}

class AppResource {
  constructor(private client: OpenSkillClient) {}

  /** List apps for the current developer */
  async list(query?: {
    page?: number;
    per_page?: number;
    category?: string;
    status?: string;
  }): Promise<ListResponse<App>> {
    return this.client.request<ListResponse<App>>("/developer/apps", {
      query: query as Record<string, string | number>,
    });
  }

  /** Get app details */
  async get(appId: string): Promise<App> {
    const res = await this.client.request<DataResponse<App>>(
      `/developer/apps/${appId}`,
    );
    return res.data;
  }

  /** Create a new app */
  async create(data: {
    name: string;
    slug: string;
    category: string;
    description?: string;
    visibility?: string;
    manifest?: Record<string, unknown>;
  }): Promise<App> {
    const res = await this.client.request<DataResponse<App>>(
      "/developer/apps",
      { method: "POST", body: data },
    );
    return res.data;
  }

  /** Update an app */
  async update(
    appId: string,
    data: Partial<{
      name: string;
      description: string;
      visibility: string;
      manifest: Record<string, unknown>;
    }>,
  ): Promise<App> {
    const res = await this.client.request<DataResponse<App>>(
      `/developer/apps/${appId}`,
      { method: "PATCH", body: data },
    );
    return res.data;
  }

  /** Create a new version */
  async createVersion(
    appId: string,
    data: {
      version: string;
      manifest: Record<string, unknown>;
      content_hash: string;
      changelog?: string;
      signature?: string;
    },
  ): Promise<AppVersion> {
    const res = await this.client.request<DataResponse<AppVersion>>(
      `/developer/apps/${appId}/versions`,
      { method: "POST", body: data },
    );
    return res.data;
  }

  /** List versions */
  async listVersions(
    appId: string,
    query?: { page?: number; per_page?: number },
  ): Promise<ListResponse<AppVersion>> {
    return this.client.request<ListResponse<AppVersion>>(
      `/developer/apps/${appId}/versions`,
      { query: query as Record<string, number> },
    );
  }

  /** Submit for review */
  async submitForReview(appId: string): Promise<App> {
    const res = await this.client.request<DataResponse<App>>(
      `/developer/apps/${appId}/submit`,
      { method: "POST" },
    );
    return res.data;
  }

  /** Publish an approved app */
  async publish(appId: string): Promise<App> {
    const res = await this.client.request<DataResponse<App>>(
      `/developer/apps/${appId}/publish`,
      { method: "POST" },
    );
    return res.data;
  }

  /** Create an API key */
  async createApiKey(
    appId: string,
    data: { name: string; scopes?: string[] },
  ): Promise<{ id: string; key: string; key_prefix: string }> {
    const res = await this.client.request<
      DataResponse<{ id: string; key: string; key_prefix: string }>
    >(`/developer/apps/${appId}/api-keys`, { method: "POST", body: data });
    return res.data;
  }

  /** List API keys */
  async listApiKeys(appId: string): Promise<ApiKey[]> {
    const res = await this.client.request<DataResponse<ApiKey[]>>(
      `/developer/apps/${appId}/api-keys`,
    );
    return res.data;
  }

  /** Get app stats */
  async getStats(appId: string): Promise<Record<string, unknown>> {
    const res = await this.client.request<DataResponse<Record<string, unknown>>>(
      `/developer/apps/${appId}/stats`,
    );
    return res.data;
  }

  /** Run conformance checks */
  async runConformance(appId: string): Promise<Record<string, unknown>> {
    const res = await this.client.request<DataResponse<Record<string, unknown>>>(
      `/developer/apps/${appId}/conformance`,
    );
    return res.data;
  }
}

class MarketplaceResource {
  constructor(private client: OpenSkillClient) {}

  /** Browse published apps */
  async browse(query?: {
    q?: string;
    category?: string;
    page?: number;
    per_page?: number;
  }): Promise<ListResponse<App>> {
    return this.client.request<ListResponse<App>>("/marketplace/apps", {
      query: query as Record<string, string | number>,
    });
  }

  /** Get a published app's details */
  async get(appId: string): Promise<App> {
    const res = await this.client.request<DataResponse<App>>(
      `/marketplace/apps/${appId}`,
    );
    return res.data;
  }
}

class CrudResource<T> {
  constructor(
    private client: OpenSkillClient,
    private resourceName: string,
  ) {}

  /** List resources for an org */
  async list(
    orgId: string,
    query?: { page?: number; per_page?: number },
  ): Promise<ListResponse<T>> {
    return this.client.request<ListResponse<T>>(
      `/orgs/${orgId}/${this.resourceName}`,
      { query: query as Record<string, number> },
    );
  }

  /** Get a single resource */
  async get(orgId: string, id: string): Promise<T> {
    const res = await this.client.request<DataResponse<T>>(
      `/orgs/${orgId}/${this.resourceName}/${id}`,
    );
    return res.data;
  }
}
