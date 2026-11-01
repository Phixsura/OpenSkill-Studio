import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectorAuthPanel } from "@/components/connector-auth-panel";

const mockCreds = [
  { id: "c1", connectorId: "slack", connectorName: "Slack", authType: "oauth2" as const,
    status: "connected" as const, scopes: ["chat:write", "users:read"], expired: false },
  { id: "c2", connectorId: "github", connectorName: "GitHub", authType: "oauth2" as const,
    status: "expired" as const, scopes: ["repo"], expired: true },
  { id: "c3", connectorId: "jira", connectorName: "Jira", authType: "api_key" as const,
    status: "disconnected" as const, scopes: [], expired: false },
];

describe("ConnectorAuthPanel", () => {
  it("renders credentials with status", () => {
    const { container } = render(<ConnectorAuthPanel credentials={mockCreds} />);
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("Connected");
    expect(container.textContent).toContain("1/3 connected");
  });

  it("shows scopes", () => {
    const { container } = render(<ConnectorAuthPanel credentials={mockCreds} />);
    expect(container.textContent).toContain("chat:write");
    expect(container.textContent).toContain("users:read");
  });

  it("calls onRefresh for expired", () => {
    const onRefresh = vi.fn();
    const { getByText } = render(<ConnectorAuthPanel credentials={mockCreds} onRefresh={onRefresh} />);
    fireEvent.click(getByText("Refresh"));
    expect(onRefresh).toHaveBeenCalledWith("c2");
  });

  it("calls onConnect for disconnected", () => {
    const onConnect = vi.fn();
    const { getByText } = render(<ConnectorAuthPanel credentials={mockCreds} onConnect={onConnect} />);
    fireEvent.click(getByText("Connect"));
    expect(onConnect).toHaveBeenCalledWith("jira");
  });
});
