import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPISecurityDashboardCard from "../src/components/api-developer-api-security-dashboard-card";

const dash = { security_score: 95, total_findings: 10, critical_findings: 0, high_findings: 2, resolved_findings: 8, active_api_keys: 25, expired_keys: 3, ip_rules: 5, cors_policies: 2 };

describe("APIDeveloperAPISecurityDashboardCard", () => {
  it("shows security metrics", () => {
    const { container } = render(<APIDeveloperAPISecurityDashboardCard dashboard={dash} isSecure={true} appName="App" />);
    expect(container.textContent).toContain("Security Dashboard");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("Secure");
    expect(container.textContent).toContain("25");
  });
});
