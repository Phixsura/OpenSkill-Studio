import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiComplianceReportCard from "../src/components/api-developer-api-api-compliance-report-card";

const frameworks = { SOC2: { compliant: 8, non_compliant: 2, pending: 1 }, GDPR: { compliant: 5, non_compliant: 0, pending: 0 } };

describe("APIDeveloperAPIApiComplianceReportCard", () => {
  it("shows compliance", () => {
    const { container } = render(<APIDeveloperAPIApiComplianceReportCard frameworks={frameworks} overallRate={86.7} nonCompliantCount={2} appName="App" />);
    expect(container.textContent).toContain("Compliance Report");
    expect(container.textContent).toContain("86.7%");
    expect(container.textContent).toContain("2 non-compliant");
    expect(container.textContent).toContain("SOC2");
    expect(container.textContent).toContain("GDPR");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiComplianceReportCard frameworks={{}} overallRate={100} nonCompliantCount={0} appName="App" />);
    expect(container.textContent).toContain("No compliance checks");
  });
});
