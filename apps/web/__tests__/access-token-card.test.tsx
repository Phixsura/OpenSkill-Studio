import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccessTokenCard } from "@/components/access-token-card";

describe("AccessTokenCard", () => {
  it("renders token info", () => {
    const { container } = render(
      <AccessTokenCard prefix="osk_abc" scopes={["read", "write"]} issuedAt="2026-01-01"
        expiresAt="2027-01-01" onRevoke={vi.fn()} />
    );
    expect(container.textContent).toContain("osk_abc");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
    expect(container.textContent).toContain("Revoke");
  });
  it("revoke click", () => {
    const fn = vi.fn();
    const { container } = render(
      <AccessTokenCard prefix="x" scopes={[]} issuedAt="2026-01-01"
        expiresAt="2027-01-01" onRevoke={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
