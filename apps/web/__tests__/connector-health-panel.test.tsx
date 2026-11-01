import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectorHealthPanel } from "@/components/connector-health-panel";

const mockConnectors = [
  { connectorId: "c1", name: "Slack API", endpointUrl: "https://slack.com/api",
    status: "healthy" as const, uptimePercent: 99.95, avgResponseMs: 120, meetsSla: true },
  { connectorId: "c2", name: "GitHub API", endpointUrl: "https://api.github.com",
    status: "degraded" as const, uptimePercent: 98.5, avgResponseMs: 2500, meetsSla: false },
  { connectorId: "c3", name: "Dead Service", endpointUrl: "https://dead.example.com",
    status: "down" as const, uptimePercent: 45.0, avgResponseMs: 0, meetsSla: false },
];

describe("ConnectorHealthPanel", () => {
  it("renders connectors with status", () => {
    const { container } = render(<ConnectorHealthPanel connectors={mockConnectors} />);
    expect(container.textContent).toContain("Slack API");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("1/3 healthy");
  });

  it("shows uptime and SLA", () => {
    const { container } = render(<ConnectorHealthPanel connectors={mockConnectors} />);
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("✓ Met");
    expect(container.textContent).toContain("✗ Breach");
  });

  it("calls onRefresh", () => {
    const onRefresh = vi.fn();
    const { getAllByText } = render(<ConnectorHealthPanel connectors={mockConnectors} onRefresh={onRefresh} />);
    fireEvent.click(getAllByText("Check")[0]);
    expect(onRefresh).toHaveBeenCalledWith("c1");
  });
});
