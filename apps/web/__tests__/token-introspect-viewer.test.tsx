import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenIntrospectViewer } from "@/components/token-introspect-viewer";

describe("TokenIntrospectViewer", () => {
  it("renders", () => {
    const { container } = render(
      <TokenIntrospectViewer active={true} expired={false} subject="user:123"
        issuer="auth.example.com" scopes={["read", "write"]} tokenType="bearer"
        authorized={false} missingScopes={["admin"]} />
    );
    expect(container.textContent).toContain("Token Introspection");
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("user:123");
    expect(container.textContent).toContain("auth.example.com");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
    expect(container.textContent).toContain("Missing: admin");
  });
});
