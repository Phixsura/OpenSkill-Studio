import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyDisplayCard } from "@/components/api-key-display-card";

describe("ApiKeyDisplayCard", () => {
  it("renders masked key", () => {
    const { container, getByText } = render(
      <ApiKeyDisplayCard name="Production" masked="sk_live_•••••" fullKey="sk_live_abc123"
        scopes={["read", "write"]} lastUsed="5m ago" onRevoke={vi.fn()} />
    );
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("sk_live_•••••");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("5m ago");
    fireEvent.click(getByText("👁️"));
    expect(container.textContent).toContain("sk_live_abc123");
  });
});
