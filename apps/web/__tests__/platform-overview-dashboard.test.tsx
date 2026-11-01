import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOverviewDashboard } from "@/components/platform-overview-dashboard";

const mockStats = {
  totalExtensions: 250, activeInstalls: 45000, totalDevelopers: 1200,
  monthlyRevenueCents: 5000000, apiCallsToday: 2500000,
  uptimePercent: 99.95, avgResponseMs: 42, openIssues: 3,
};
const mockSystems = [
  { name: "API Gateway", status: "healthy" as const },
  { name: "Sandbox Runtime", status: "healthy" as const },
  { name: "Webhook Delivery", status: "degraded" as const },
  { name: "Search Index", status: "healthy" as const },
];

describe("PlatformOverviewDashboard", () => {
  it("renders stats cards", () => {
    const { container } = render(
      <PlatformOverviewDashboard stats={mockStats} systems={mockSystems} />
    );
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("45,000");
    expect(container.textContent).toContain("$50,000");
    expect(container.textContent).toContain("1200");
  });

  it("shows operational metrics", () => {
    const { container } = render(
      <PlatformOverviewDashboard stats={mockStats} systems={mockSystems} />
    );
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("42ms");
    expect(container.textContent).toContain("2,500,000");
  });

  it("shows system health", () => {
    const { container } = render(
      <PlatformOverviewDashboard stats={mockStats} systems={mockSystems} />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("Webhook Delivery");
    expect(container.textContent).toContain("3/4 healthy");
  });
});
