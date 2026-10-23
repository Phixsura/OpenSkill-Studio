import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyManagerPanel } from "@/components/api-key-manager-panel";

describe("ApiKeyManagerPanel", () => {
  const keys = [
    { prefix: "sk_abc1", label: "Prod", scopes: ["read", "write"], created_at: "2026-01-01", last_used: null, status: "active" },
  ];
  it("renders keys", () => {
    const { container } = render(<ApiKeyManagerPanel keys={keys} onRevoke={vi.fn()} onCreate={vi.fn()} />);
    expect(container.textContent).toContain("API Keys");
    expect(container.textContent).toContain("Prod");
    expect(container.textContent).toContain("sk_abc1");
  });
  it("revoke", () => {
    const fn = vi.fn();
    const { container } = render(<ApiKeyManagerPanel keys={keys} onRevoke={fn} onCreate={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Revoke")!);
    expect(fn).toHaveBeenCalledWith("sk_abc1");
  });
});
