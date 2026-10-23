import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceAuditCard } from "@/components/compliance-audit-card";

describe("ComplianceAuditCard", () => {
  it("renders audit", () => {
    const rules = [
      { id: "enc", label: "Data encrypted", category: "security", severity: "critical", passed: true },
      { id: "log", label: "Access logging", category: "audit", severity: "high", passed: false },
    ];
    const { container } = render(<ComplianceAuditCard rules={rules} score={50} compliant={false} criticalFailures={0} />);
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Data encrypted");
    expect(container.textContent).toContain("Access logging");
  });
  it("shows critical", () => {
    const { container } = render(<ComplianceAuditCard rules={[]} score={25} compliant={false} criticalFailures={2} />);
    expect(container.textContent).toContain("2 critical");
  });
});
