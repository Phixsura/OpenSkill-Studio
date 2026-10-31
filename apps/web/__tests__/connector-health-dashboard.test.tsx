import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConnectorHealthDashboard } from "@/components/connector-health-dashboard";

const mockConnectors = [
  { id: "slack", name: "Slack", icon: "💬", status: "operational" as const, uptimePercent: 99.99, avgLatencyMs: 42, lastIncident: "30d ago", eventsLast24h: 12500, errorRate: 0.1 },
  { id: "github", name: "GitHub", icon: "🐙", status: "degraded" as const, uptimePercent: 99.5, avgLatencyMs: 185, lastIncident: "2h ago", eventsLast24h: 8000, errorRate: 2.3 },
  { id: "jira", name: "Jira", icon: "📋", status: "outage" as const, uptimePercent: 95.2, avgLatencyMs: 0, lastIncident: "now", eventsLast24h: 200, errorRate: 45.0 },
];

describe("ConnectorHealthDashboard", () => {
  it("renders connectors with status", () => {
    const { container } = render(
      <ConnectorHealthDashboard connectors={mockConnectors} overallStatus="degraded" />
    );
    expect(container.textContent).toContain("Connector Health");
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("Operational");
    expect(container.textContent).toContain("Degraded");
    expect(container.textContent).toContain("Outage");
  });

  it("shows operational count", () => {
    const { container } = render(
      <ConnectorHealthDashboard connectors={mockConnectors} overallStatus="degraded" />
    );
    expect(container.textContent).toContain("1/3 operational");
  });

  it("shows uptime and latency", () => {
    const { container } = render(
      <ConnectorHealthDashboard connectors={mockConnectors} overallStatus="operational" />
    );
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("42ms");
    expect(container.textContent).toContain("12,500");
  });

  it("highlights high error rates", () => {
    const { container } = render(
      <ConnectorHealthDashboard connectors={mockConnectors} overallStatus="degraded" />
    );
    expect(container.textContent).toContain("45%");
    expect(container.textContent).toContain("0.1%");
  });
});
