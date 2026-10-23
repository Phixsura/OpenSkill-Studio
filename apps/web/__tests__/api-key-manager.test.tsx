import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyManager } from "@/components/api-key-manager";

describe("ApiKeyManager", () => {
  const keys = [
    { prefix: "osk_abcd", name: "Prod Key", scopes: ["read", "write"], created_at: "2026-01-01", revoked: false },
    { prefix: "osk_efgh", name: "Old Key", scopes: ["read"], created_at: "2025-06-01", revoked: true },
  ];
  it("renders keys", () => {
    const { container } = render(<ApiKeyManager keys={keys} onRevoke={vi.fn()} />);
    expect(container.textContent).toContain("Prod Key");
    expect(container.textContent).toContain("osk_abcd");
    expect(container.textContent).toContain("Revoked");
    expect(container.textContent).toContain("1 active");
  });
  it("revoke click", () => {
    const fn = vi.fn();
    const { container } = render(<ApiKeyManager keys={keys} onRevoke={fn} />);
    const btn = container.querySelector("button")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("osk_abcd");
  });
});
