import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IntegrationList } from "@/components/integration-list";

describe("IntegrationList", () => {
  const integrations = [
    { id: "github", label: "GitHub", icon: "🐙", category: "SCM", connected: true },
    { id: "stripe", label: "Stripe", icon: "💳", category: "Payments", connected: false },
  ];
  it("renders integrations", () => {
    const { container } = render(
      <IntegrationList integrations={integrations} connected={1} onConnect={vi.fn()} onDisconnect={vi.fn()} />
    );
    expect(container.textContent).toContain("GitHub");
    expect(container.textContent).toContain("Stripe");
    expect(container.textContent).toContain("1 connected");
    expect(container.textContent).toContain("Connect");
    expect(container.textContent).toContain("Disconnect");
  });
  it("connect click", () => {
    const fn = vi.fn();
    const { container } = render(
      <IntegrationList integrations={integrations} connected={1} onConnect={fn} onDisconnect={vi.fn()} />
    );
    const connectBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Connect")!;
    fireEvent.click(connectBtn);
    expect(fn).toHaveBeenCalledWith("stripe");
  });
});
