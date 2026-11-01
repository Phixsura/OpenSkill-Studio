import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TokenRefreshStatus } from "@/components/token-refresh-status";

describe("TokenRefreshStatus", () => {
  it("shows active tokens", () => {
    const { container } = render(
      <TokenRefreshStatus accessExpiresAt="2099-01-01" refreshExpiresAt="2099-01-01"
        tokenType="Bearer" onRefresh={vi.fn()} />
    );
    expect(container.textContent).toContain("Token Status");
    expect(container.textContent).toContain("Bearer");
    expect(container.textContent).toContain("remaining");
  });
  it("shows expired access", () => {
    const { container } = render(
      <TokenRefreshStatus accessExpiresAt="2020-01-01" refreshExpiresAt="2099-01-01"
        tokenType="Bearer" onRefresh={vi.fn()} />
    );
    expect(container.textContent).toContain("Expired");
    expect(container.textContent).toContain("Refresh Token");
  });
});
