import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ComplianceAuditCard from "../src/components/compliance-audit-card";

const findings = [
  {
    finding_id: "f1",
    category: "security",
    severity: "high" as const,
    description: "Exposed API key",
    remediated: true,
  },
  {
    finding_id: "f2",
    category: "data",
    severity: "critical" as const,
    description: "PII in logs",
    remediated: false,
  },
];

describe("ComplianceAuditCard", () => {
  it("renders header", () => {
    const { container } = render(
      <ComplianceAuditCard findings={findings} complianceScore={50} appName="My App" />,
    );
    expect(container.textContent).toContain("Compliance Audit");
  });

  it("shows compliance score", () => {
    const { container } = render(
      <ComplianceAuditCard findings={findings} complianceScore={50} appName="App" />,
    );
    expect(container.textContent).toContain("50%");
  });

  it("shows open count", () => {
    const { container } = render(
      <ComplianceAuditCard findings={findings} complianceScore={50} appName="App" />,
    );
    expect(container.textContent).toContain("1 open");
  });

  it("renders findings with severity", () => {
    const { container } = render(
      <ComplianceAuditCard findings={findings} complianceScore={50} appName="App" />,
    );
    expect(container.textContent).toContain("PII in logs");
    expect(container.textContent).toContain("critical");
  });

  it("shows remediated indicator", () => {
    const { container } = render(
      <ComplianceAuditCard findings={findings} complianceScore={50} appName="App" />,
    );
    expect(container.textContent).toContain("fixed");
  });

  it("shows no-findings message", () => {
    const { container } = render(
      <ComplianceAuditCard findings={[]} complianceScore={100} appName="App" />,
    );
    expect(container.textContent).toContain("No findings");
  });
});
