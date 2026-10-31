import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPISLAComplianceTrackerCard from "../src/components/api-developer-api-sla-compliance-tracker-card";

const targets = [
  { endpoint: "/api/users", uptime_target_pct: 99.9, actual_uptime_pct: 99.95, latency_p99_target_ms: 200, actual_latency_p99_ms: 150, compliant: true, violation_rate_pct: 0 },
  { endpoint: "/api/payments", uptime_target_pct: 99.99, actual_uptime_pct: 99.0, latency_p99_target_ms: 100, actual_latency_p99_ms: 300, compliant: false, violation_rate_pct: 50 },
];

describe("APIDeveloperAPISLAComplianceTrackerCard", () => {
  it("shows SLA compliance", () => {
    const { container } = render(<APIDeveloperAPISLAComplianceTrackerCard targets={targets} nonCompliantCount={1} appName="App" />);
    expect(container.textContent).toContain("SLA Compliance");
    expect(container.textContent).toContain("1 breached");
    expect(container.textContent).toContain("uptime: 99.95%");
    expect(container.textContent).toContain("p99: 300ms");
  });
  it("shows all compliant", () => {
    const { container } = render(<APIDeveloperAPISLAComplianceTrackerCard targets={[]} nonCompliantCount={0} appName="App" />);
    expect(container.textContent).toContain("all compliant");
  });
});
