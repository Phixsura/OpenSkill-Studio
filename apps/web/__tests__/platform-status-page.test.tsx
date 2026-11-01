import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatusPage } from "@/components/platform-status-page";

const mockServices = [
  { name: "API Gateway", status: "operational" as const, uptime: 99.99 },
  { name: "Sandbox Runtime", status: "operational" as const, uptime: 99.95 },
  { name: "Search Index", status: "degraded" as const, uptime: 98.5 },
  { name: "Webhook Delivery", status: "operational" as const, uptime: 99.9 },
];
const mockIncidents = [
  { title: "Search latency spike", severity: "SEV2", status: "resolved", timestamp: "2h ago" },
];

describe("PlatformStatusPage", () => {
  it("renders overall status", () => {
    const { container } = render(
      <PlatformStatusPage services={mockServices} incidents={mockIncidents} overallStatus="operational" />
    );
    expect(container.textContent).toContain("All Systems operational");
  });

  it("shows service statuses", () => {
    const { container } = render(
      <PlatformStatusPage services={mockServices} incidents={[]} overallStatus="operational" />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("99.99% uptime");
    expect(container.textContent).toContain("degraded");
  });

  it("shows incidents", () => {
    const { container } = render(
      <PlatformStatusPage services={mockServices} incidents={mockIncidents} overallStatus="degraded" />
    );
    expect(container.textContent).toContain("Search latency spike");
    expect(container.textContent).toContain("SEV2");
    expect(container.textContent).toContain("resolved");
  });

  it("renders outage state", () => {
    const { container } = render(
      <PlatformStatusPage services={[]} incidents={[]} overallStatus="outage" />
    );
    expect(container.textContent).toContain("outage");
  });
});
