import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OAuthConnectButton } from "@/components/oauth-connect-button";

describe("OAuthConnectButton", () => {
  const provider = { id: "github", name: "GitHub", icon: "🐙", color: "#333" };
  it("shows connect when not connected", () => {
    const { container } = render(
      <OAuthConnectButton provider={provider} connected={false} onConnect={vi.fn()} onDisconnect={vi.fn()} />
    );
    expect(container.textContent).toContain("Not connected");
    expect(container.textContent).toContain("Connect");
  });
  it("shows disconnect when connected", () => {
    const fn = vi.fn();
    const { container } = render(
      <OAuthConnectButton provider={provider} connected={true} onConnect={vi.fn()} onDisconnect={fn} />
    );
    expect(container.textContent).toContain("Connected");
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
