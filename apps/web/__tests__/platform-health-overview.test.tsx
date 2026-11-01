import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformHealthOverview } from "@/components/platform-health-overview";

const mockServices = [
  { name: "API Gateway", status: "healthy" as const, latencyMs: 42, uptime: 99.99 },
  { name: "Sandbox Runtime", status: "healthy" as const, latencyMs: 85, uptime: 99.95 },
  { name: "Webhook Delivery", status: "degraded" as const, latencyMs: 250, uptime: 99.5 },
  { name: "Search Engine", status: "healthy" as const, latencyMs: 35, uptime: 100 },
];

const mockMetrics = {
  totalExtensions: 245, activeOrgs: 120, apiCallsToday: 1250000,
  errorRate: 0.3, avgLatencyMs: 65,
};

describe("PlatformHealthOverview", () => {
  it("renders overall status", () => {
    const { container } = render(
      <PlatformHealthOverview services={mockServices} metrics={mockMetrics} lastUpdated="30s ago" />
    );
    expect(container.textContent).toContain("1 Service(s) Degraded");
    expect(container.textContent).toContain("30s ago");
  });

  it("renders metrics", () => {
    const { container } = render(
      <PlatformHealthOverview services={mockServices} metrics={mockMetrics} lastUpdated="now" />
    );
    expect(container.textContent).toContain("245");
    expect(container.textContent).toContain("1,250,000");
    expect(container.textContent).toContain("0.3%");
    expect(container.textContent).toContain("65ms");
  });

  it("renders services with status", () => {
    const { container } = render(
      <PlatformHealthOverview services={mockServices} metrics={mockMetrics} lastUpdated="now" />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("Webhook Delivery");
    expect(container.textContent).toContain("3/4 healthy");
  });

  it("shows all operational when healthy", () => {
    const allHealthy = mockServices.map((s) => ({ ...s, status: "healthy" as const }));
    const { container } = render(
      <PlatformHealthOverview services={allHealthy} metrics={mockMetrics} lastUpdated="now" />
    );
    expect(container.textContent).toContain("All Systems Operational");
  });
});
