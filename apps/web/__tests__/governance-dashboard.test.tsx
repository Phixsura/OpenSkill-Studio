import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GovernanceDashboard } from "@/components/governance-dashboard";

describe("GovernanceDashboard", () => {
  it("renders governance", () => {
    const { container } = render(
      <GovernanceDashboard score={67} violations={2} criticalViolations={1} compliant={false}
        results={[
          { policy: "code_review", description: "Code review required", severity: "high", passed: true },
          { policy: "security_scan", description: "Security scan", severity: "critical", passed: false },
          { policy: "docs", description: "Documentation", severity: "medium", passed: false },
        ]} />
    );
    expect(container.textContent).toContain("Governance");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("2 violations");
    expect(container.textContent).toContain("Code review");
    expect(container.textContent).toContain("Security scan");
    expect(container.textContent).toContain("critical");
  });
});
