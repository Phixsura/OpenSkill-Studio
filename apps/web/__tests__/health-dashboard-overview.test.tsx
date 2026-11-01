import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthDashboardOverview } from "@/components/health-dashboard-overview";

const mockSummary = {
  totalServices: 10, overallScore: 82, overallState: "degraded",
  byState: { healthy: 7, degraded: 2, critical: 1, down: 0 }, activeIssues: 2,
};
const mockServices = [
  { name: "API Gateway", category: "infra", state: "healthy" as const, message: "" },
  { name: "Search", category: "infra", state: "degraded" as const, message: "slow" },
  { name: "Auth", category: "infra", state: "critical" as const, message: "high error rate" },
];
const mockAlerts = [
  { serviceName: "Auth", severity: "high" as const, message: "Auth service critical",
    suggestedAction: "Check auth server logs" },
];

describe("HealthDashboardOverview", () => {
  it("renders health score", () => {
    const { container } = render(
      <HealthDashboardOverview summary={mockSummary} services={mockServices} alerts={mockAlerts} />
    );
    expect(container.textContent).toContain("82");
    expect(container.textContent).toContain("/ 100");
  });

  it("shows state counts", () => {
    const { container } = render(
      <HealthDashboardOverview summary={mockSummary} services={mockServices} alerts={mockAlerts} />
    );
    expect(container.textContent).toContain("7");
    expect(container.textContent).toContain("2");
  });

  it("shows alerts with actions", () => {
    const { container } = render(
      <HealthDashboardOverview summary={mockSummary} services={mockServices} alerts={mockAlerts} />
    );
    expect(container.textContent).toContain("Auth service critical");
    expect(container.textContent).toContain("Check auth server logs");
  });

  it("renders service grid", () => {
    const { container } = render(
      <HealthDashboardOverview summary={mockSummary} services={mockServices} alerts={[]} />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("Search");
  });
});
