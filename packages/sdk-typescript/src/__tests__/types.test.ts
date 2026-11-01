import { describe, test, expect } from "vitest";
import type {
  App,
  AppVersion,
  AppInstallation,
  DeveloperAccount,
  ApiKey,
  Manifest,
  Permission,
  AppCategory,
  AppStatus,
  DataResponse,
  ListResponse,
  ErrorResponse,
} from "../types.js";

describe("Type definitions", () => {
  test("Permission type covers expected scopes", () => {
    const perms: Permission[] = [
      "read:cohorts",
      "write:projects",
      "subscribe:events",
      "extend:ui",
      "run:background_jobs",
    ];
    expect(perms).toHaveLength(5);
  });

  test("AppCategory covers all types", () => {
    const categories: AppCategory[] = [
      "connector",
      "workflow_adapter",
      "ui_extension",
      "analytics",
      "automation",
      "content_pack",
      "ecosystem_source",
    ];
    expect(categories).toHaveLength(7);
  });

  test("AppStatus covers lifecycle", () => {
    const statuses: AppStatus[] = [
      "draft",
      "testing",
      "submitted",
      "approved",
      "published",
      "deprecated",
      "revoked",
    ];
    expect(statuses).toHaveLength(7);
  });

  test("Manifest structure is valid", () => {
    const manifest: Manifest = {
      schema_version: "1.0",
      app: { name: "Test" },
      permissions: ["read:cohorts"],
      sandbox: {
        runtime: "nodejs20",
        memory_mb: 128,
        timeout_seconds: 30,
        network: {
          allowed_hosts: ["api.example.com"],
          egress_policy: "allowlist",
        },
      },
      ui_extensions: [
        { surface: "dashboard_card", title: "Test", entry: "card.html" },
      ],
      event_subscriptions: ["submission.completed"],
      secrets: [{ key: "API_KEY", required: true }],
    };
    expect(manifest.schema_version).toBe("1.0");
    expect(manifest.permissions).toHaveLength(1);
    expect(manifest.ui_extensions).toHaveLength(1);
  });

  test("DataResponse wraps data", () => {
    const resp: DataResponse<{ id: string }> = { data: { id: "123" } };
    expect(resp.data.id).toBe("123");
  });

  test("ListResponse has meta", () => {
    const resp: ListResponse<{ id: string }> = {
      data: [{ id: "1" }],
      meta: { total: 1, page: 1, per_page: 20, has_more: false },
    };
    expect(resp.meta.total).toBe(1);
  });

  test("ErrorResponse structure", () => {
    const resp: ErrorResponse = {
      error: { code: "TEST", message: "error" },
    };
    expect(resp.error.code).toBe("TEST");
  });
});
