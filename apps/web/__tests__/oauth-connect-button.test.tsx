import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OAuthConnectButton } from "@/components/oauth-connect-button";

const connectors = [
  { connectorId: "slack", name: "Slack", icon: "💬", connected: true, scopes: ["read", "write"] },
  { connectorId: "github", name: "GitHub", icon: "🐙", connected: false, scopes: ["repo"] },
];

describe("OAuthConnectButton", () => {
  it("renders connectors", () => {
    const { container } = render(<OAuthConnectButton connectors={connectors} />);
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("Connected ✓");
    expect(container.textContent).toContain("Connect");
  });
  it("connect action", () => {
    const fn = vi.fn();
    const { container } = render(<OAuthConnectButton connectors={connectors} onConnect={fn} />);
    const connectBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Connect");
    if (connectBtn) fireEvent.click(connectBtn);
    expect(fn).toHaveBeenCalledWith("github");
  });
});
