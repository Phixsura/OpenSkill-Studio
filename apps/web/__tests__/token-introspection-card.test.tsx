import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenIntrospectionCard } from "@/components/token-introspection-card";

describe("TokenIntrospectionCard", () => {
  it("active token", () => {
    const { container } = render(
      <TokenIntrospectionCard active={true} appId="app-1" scopes={["read", "write"]}
        issuedAt="2026-01-01" expiresAt="2027-01-01" expired={false} revoked={false} />
    );
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("app-1");
    expect(container.textContent).toContain("read");
  });
  it("revoked token", () => {
    const { container } = render(
      <TokenIntrospectionCard active={false} appId="app-1" scopes={[]}
        issuedAt="2026-01-01" expiresAt={null} expired={false} revoked={true} />
    );
    expect(container.textContent).toContain("Revoked");
  });
});
