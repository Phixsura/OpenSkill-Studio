import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComplianceRptPanel } from "@/components/compliance-rpt-panel";
describe("ComplianceRptPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ComplianceRptPanel framework="SOC2" score={66.7} compliant={false}
        passed={2} failed={1}
        failedChecks={[{ control: "AC-3", finding: "MFA not enforced" }]} />
    );
    expect(container.textContent).toContain("SOC2 Compliance");
    expect(container.textContent).toContain("66.7%");
    expect(container.textContent).toContain("1 findings");
    expect(container.textContent).toContain("AC-3");
    expect(container.textContent).toContain("MFA not enforced");
  });
});
