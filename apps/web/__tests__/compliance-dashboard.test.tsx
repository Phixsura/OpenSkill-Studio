import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceDashboard } from "@/components/compliance-dashboard";

describe("ComplianceDashboard", () => {
  it("renders compliance", () => {
    const { container } = render(
      <ComplianceDashboard overall={false} policies={{
        gdpr: { policy: "GDPR", passed: 3, total: 5, compliant: false, compliancePct: 60,
          checks: [{ check: "consent", passed: true }, { check: "deletion", passed: false }] },
        soc2: { policy: "SOC 2", passed: 5, total: 5, compliant: true, compliancePct: 100,
          checks: [{ check: "encryption", passed: true }] },
      }} />
    );
    expect(container.textContent).toContain("Compliance");
    expect(container.textContent).toContain("Action Required");
    expect(container.textContent).toContain("GDPR");
    expect(container.textContent).toContain("3/5");
    expect(container.textContent).toContain("SOC 2");
    expect(container.textContent).toContain("100%");
  });
});
