import { describe, expect, it } from "vitest";
import {
  getStatusLabel, getStatusColor, getCategoryIcon, getCategoryLabel,
  getHealthStatusColor, formatErrorRate, groupPermissions, formatPermission,
  safeUrl, compareVersions, isNewerVersion,
} from "@/lib/developer-utils";

describe("Status helpers", () => {
  it.each(["draft", "testing", "submitted", "approved", "published", "deprecated", "revoked"])(
    "getStatusLabel(%s)", (s) => expect(getStatusLabel(s)).not.toBe(s) // has a label
  );
  it("unknown status returns raw", () => expect(getStatusLabel("xyz")).toBe("xyz"));
  it.each(["draft", "published", "revoked"])("getStatusColor(%s)", (s) =>
    expect(getStatusColor(s)).not.toBe("gray")
  );
});

describe("Category helpers", () => {
  it.each(["connector", "automation", "analytics"])("getCategoryIcon(%s)", (c) =>
    expect(getCategoryIcon(c).length).toBeGreaterThan(0)
  );
  it("unknown category fallback", () => expect(getCategoryIcon("xyz")).toBe("📦"));
  it.each(["connector", "automation"])("getCategoryLabel(%s)", (c) =>
    expect(getCategoryLabel(c)).not.toBe(c)
  );
});

describe("Health helpers", () => {
  it.each([["healthy", "green"], ["degraded", "yellow"], ["warning", "orange"], ["critical", "red"]] as const)(
    "getHealthStatusColor(%s) = %s", (status, color) => expect(getHealthStatusColor(status)).toBe(color)
  );
  it("formatErrorRate", () => expect(formatErrorRate(5.123)).toBe("5.1%"));
});

describe("Permission helpers", () => {
  it("groupPermissions groups by action", () => {
    const g = groupPermissions(["read:cohorts", "read:projects", "write:cohorts"]);
    expect(g.read).toHaveLength(2);
    expect(g.write).toHaveLength(1);
  });
  it("formatPermission parses correctly", () => {
    const p = formatPermission("read:cohorts");
    expect(p.action).toBe("read");
    expect(p.resource).toBe("cohorts");
    expect(p.icon).toBe("👁️");
  });
});

describe("safeUrl", () => {
  it("accepts https", () => expect(safeUrl("https://x.com")).toBe("https://x.com"));
  it("accepts http", () => expect(safeUrl("http://x.com")).toBe("http://x.com"));
  it("rejects javascript:", () => expect(safeUrl("javascript:alert(1)")).toBeNull());
  it("rejects null", () => expect(safeUrl(null)).toBeNull());
  it("rejects empty", () => expect(safeUrl("")).toBeNull());
});

describe("Version helpers", () => {
  it("compareVersions equal", () => expect(compareVersions("1.0.0", "1.0.0")).toBe(0));
  it("compareVersions less", () => expect(compareVersions("1.0.0", "2.0.0")).toBeLessThan(0));
  it("compareVersions greater", () => expect(compareVersions("2.0.0", "1.0.0")).toBeGreaterThan(0));
  it("compareVersions patch", () => expect(compareVersions("1.0.0", "1.0.1")).toBeLessThan(0));
  it("isNewerVersion true", () => expect(isNewerVersion("1.0.0", "2.0.0")).toBe(true));
  it("isNewerVersion false", () => expect(isNewerVersion("2.0.0", "1.0.0")).toBe(false));
});
