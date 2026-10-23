import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TokenManagerPanel } from "@/components/token-manager-panel";

describe("TokenManagerPanel", () => {
  const tokens = [
    { token_hash: "abc123", scopes: ["read", "write"], expires_at: "2027-01-01T00:00:00", client_id: "app1" },
  ];
  it("renders", () => {
    const { container } = render(<TokenManagerPanel tokens={tokens} onRevoke={vi.fn()} onRefresh={vi.fn()} />);
    expect(container.textContent).toContain("Active Tokens");
    expect(container.textContent).toContain("abc123");
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("read");
  });
  it("revoke", () => {
    const fn = vi.fn();
    const { container } = render(<TokenManagerPanel tokens={tokens} onRevoke={fn} onRefresh={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Revoke")!);
    expect(fn).toHaveBeenCalledWith("abc123");
  });
});
