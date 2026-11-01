import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceTracker } from "@/components/compliance-tracker";

describe("ComplianceTracker", () => {
  it("renders", () => {
    const { container } = render(
      <ComplianceTracker overallPct={94} allCompliant={false}
        frameworks={{
          SOC2: { passed: 10, total: 10, pct: 100, compliant: true },
          GDPR: { passed: 8, total: 10, pct: 80, compliant: false },
        }} />
    );
    expect(container.textContent).toContain("Compliance Tracker");
    expect(container.textContent).toContain("94%");
    expect(container.textContent).toContain("Gaps Found");
    expect(container.textContent).toContain("SOC2");
    expect(container.textContent).toContain("10/10");
    expect(container.textContent).toContain("GDPR");
    expect(container.textContent).toContain("80%");
  });
});
