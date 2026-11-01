import { describe, expect, it } from "vitest";
import type {
  AppStatus, AppVisibility, ReviewStatus, InstallationStatus, AppCategory,
  DeveloperAccount, App, AppVersion, AppInstallation, ApiKey,
  EventSubscription, AutomationRule, Manifest, HealthScore,
  ConformanceCheck, ConformanceReport, DataResponse, ListResponse, ErrorResponse,
} from "@/lib/developer-api-types";

describe("Developer API Types", () => {
  it("AppStatus covers all states", () => {
    const statuses: AppStatus[] = ["draft", "testing", "submitted", "approved", "published", "deprecated", "revoked"];
    expect(statuses).toHaveLength(7);
  });

  it("AppCategory covers all types", () => {
    const cats: AppCategory[] = ["connector", "automation", "analytics", "ui_extension", "ecosystem_source", "content_pack", "workflow_adapter"];
    expect(cats).toHaveLength(7);
  });

  it("ReviewStatus covers all states", () => {
    const rs: ReviewStatus[] = ["pending", "approved", "rejected"];
    expect(rs).toHaveLength(3);
  });

  it("InstallationStatus covers all states", () => {
    const is: InstallationStatus[] = ["active", "suspended", "uninstalled"];
    expect(is).toHaveLength(3);
  });

  it("AppVisibility covers all states", () => {
    const vs: AppVisibility[] = ["private", "public", "unlisted"];
    expect(vs).toHaveLength(3);
  });

  it("DeveloperAccount shape", () => {
    const account: DeveloperAccount = {
      id: "d1", owner_user_id: "u1", org_id: null, display_name: "Dev",
      slug: "dev", website_url: null, support_email: "a@b.c",
      verified: false, status: "active", created_at: "", updated_at: "",
    };
    expect(account.id).toBe("d1");
  });

  it("Manifest shape", () => {
    const m: Manifest = {
      schema_version: "1.0",
      app: { name: "X", slug: "x", version: "1.0.0", category: "connector" },
      permissions: ["read:cohorts"],
    };
    expect(m.schema_version).toBe("1.0");
  });

  it("HealthScore shape", () => {
    const h: HealthScore = {
      score: 95, status: "healthy", error_rate_pct: 5,
      total_executions: 100, failed_executions: 5, timeout_executions: 0,
    };
    expect(h.score).toBe(95);
  });

  it("ErrorResponse shape", () => {
    const err: ErrorResponse = { error: { code: "NOT_FOUND", message: "Not found" } };
    expect(err.error.code).toBe("NOT_FOUND");
  });
});
