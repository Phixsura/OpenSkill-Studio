import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DepAuditPanel } from "@/components/dep-audit-panel";

const mockSummary = {
  passed: false, totalDeps: 5, vulnsCritical: 1, vulnsHigh: 1,
  vulnsMedium: 2, vulnsLow: 0, licenseIssues: 1, outdated: 2,
};
const mockDeps = [
  { name: "lodash", version: "4.17.20", license: "MIT", licenseRisk: "permissive" as const,
    isOutdated: true, latestVersion: "4.17.21", vulnCount: 1, highestSeverity: "high" as const },
  { name: "gpl-lib", version: "1.0", license: "GPL-3.0", licenseRisk: "strong_copyleft" as const,
    isOutdated: false, latestVersion: "1.0", vulnCount: 0 },
];

describe("DepAuditPanel", () => {
  it("renders audit summary", () => {
    const { container } = render(
      <DepAuditPanel summary={mockSummary} dependencies={mockDeps} />
    );
    expect(container.textContent).toContain("Failed");
    expect(container.textContent).toContain("5");
  });

  it("shows dependencies with vulns", () => {
    const { container } = render(
      <DepAuditPanel summary={mockSummary} dependencies={mockDeps} />
    );
    expect(container.textContent).toContain("lodash");
    expect(container.textContent).toContain("1 vuln");
    expect(container.textContent).toContain("→ 4.17.21");
  });

  it("shows license risk", () => {
    const { container } = render(
      <DepAuditPanel summary={mockSummary} dependencies={mockDeps} />
    );
    expect(container.textContent).toContain("GPL-3.0");
  });

  it("calls onRescan", () => {
    const onRescan = vi.fn();
    const { getByText } = render(
      <DepAuditPanel summary={mockSummary} dependencies={mockDeps} onRescan={onRescan} />
    );
    fireEvent.click(getByText("Rescan"));
    expect(onRescan).toHaveBeenCalled();
  });
});
