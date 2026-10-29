import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPICircuitBreakerDashboardCard from "../src/components/api-developer-api-circuit-breaker-dashboard-card";

const circuits = [
  { endpoint: "/api/users", state: "closed", failure_count: 1, success_count: 99, failure_rate: 1 },
  { endpoint: "/api/payments", state: "open", failure_count: 10, success_count: 5, failure_rate: 66.7 },
];

describe("APIDeveloperAPICircuitBreakerDashboardCard", () => {
  it("shows circuits", () => {
    const { container } = render(<APIDeveloperAPICircuitBreakerDashboardCard circuits={circuits} openCount={1} appName="App" />);
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("/api/payments");
    expect(container.textContent).toContain("66.7% fail");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPICircuitBreakerDashboardCard circuits={[]} openCount={0} appName="App" />);
    expect(container.textContent).toContain("No circuits");
  });
});
