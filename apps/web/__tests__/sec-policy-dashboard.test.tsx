import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecPolicyDashboard } from "@/components/sec-policy-dashboard";

describe("SecPolicyDashboard", () => {
  it("renders violations", () => {
    const { container } = render(
      <SecPolicyDashboard resourceName="api-server" compliant={false}
        riskLevel="high" riskScore={12}
        violations={[
          { policy: "encrypt_at_rest", description: "Encrypt data", severity: "high" },
          { policy: "audit_logging", description: "Enable logging", severity: "high" },
        ]} />
    );
    expect(container.textContent).toContain("Security: api-server");
    expect(container.textContent).toContain("2 violations");
    expect(container.textContent).toContain("encrypt_at_rest");
    expect(container.textContent).toContain("high");
    expect(container.textContent).toContain("score 12");
  });
});
