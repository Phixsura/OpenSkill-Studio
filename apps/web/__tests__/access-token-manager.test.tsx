import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccessTokenManager } from "@/components/access-token-manager";

describe("AccessTokenManager", () => {
  it("renders tokens", () => {
    const { container } = render(
      <AccessTokenManager onIssue={vi.fn()} onRevoke={vi.fn()} tokens={[
        { subject: "user:123", scopes: ["read", "write"], expiresIn: 3600 },
        { subject: "service:api", scopes: ["admin"], expiresIn: 7200 },
      ]} />
    );
    expect(container.textContent).toContain("Access Tokens");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("user:123");
    expect(container.textContent).toContain("read, write");
    expect(container.textContent).toContain("service:api");
    expect(container.textContent).toContain("Issue");
  });
});
