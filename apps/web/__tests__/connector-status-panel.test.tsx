import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectorStatusPanel } from "@/components/connector-status-panel";

const mockConnectors = [
  { id: "slack", name: "Slack", icon: "💬", status: "connected" as const, lastSync: "2m ago", eventsProcessed: 1500, errorCount: 0, latencyMs: 45 },
  { id: "github", name: "GitHub", icon: "🐙", status: "error" as const, lastSync: "1h ago", eventsProcessed: 800, errorCount: 3, latencyMs: 120 },
  { id: "jira", name: "Jira", icon: "📋", status: "disconnected" as const, lastSync: "Never", eventsProcessed: 0, errorCount: 0, latencyMs: 0 },
];

describe("ConnectorStatusPanel", () => {
  it("renders all connectors with status", () => {
    const { container } = render(<ConnectorStatusPanel connectors={mockConnectors} />);
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("Connected");
    expect(container.textContent).toContain("Error");
    expect(container.textContent).toContain("1/3 connected");
  });

  it("shows error count", () => {
    const { container } = render(<ConnectorStatusPanel connectors={mockConnectors} />);
    expect(container.textContent).toContain("3 errors");
  });

  it("shows disconnect for connected, reconnect for others", () => {
    const onReconnect = vi.fn();
    const { getByText, getAllByText } = render(
      <ConnectorStatusPanel connectors={mockConnectors} onReconnect={onReconnect} />
    );
    expect(getByText("Disconnect")).toBeDefined();
    const reconnectBtns = getAllByText("Reconnect");
    expect(reconnectBtns.length).toBe(2);
    fireEvent.click(reconnectBtns[0]);
    expect(onReconnect).toHaveBeenCalledWith("github");
  });
});
