import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditComplianceCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-audit-compliance-card";

const frameworks = [{ framework: "SOC2", total_controls: 100, compliance_pct: 96.9, assessment_pct: 98, audit_ready: true }];

describe("Card", () => {
  it("shows audit compliance", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditComplianceCard frameworks={frameworks} overallCompliance={96.9} auditReadyCount={1} appName="App" />);
    expect(container.textContent).toContain("Audit Compliance");
    expect(container.textContent).toContain("96.9% overall");
    expect(container.textContent).toContain("1 audit ready");
    expect(container.textContent).toContain("SOC2");
    expect(container.textContent).toContain("100 controls");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformAuditComplianceCard frameworks={[]} overallCompliance={0} auditReadyCount={0} appName="App" />);
    expect(container.textContent).toContain("No compliance frameworks");
  });
});
