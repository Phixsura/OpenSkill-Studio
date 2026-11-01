import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiTokenScopeManagerCard from "../src/components/api-developer-api-api-token-scope-manager-card";

const tokens = [
  { token_id: "t1", name: "CI Token", scopes: ["read", "webhooks:read"], revoked: false },
  { token_id: "t2", name: "Old Token", scopes: ["admin"], revoked: true },
];

describe("APIDeveloperAPIApiTokenScopeManagerCard", () => {
  it("shows tokens", () => {
    const { container } = render(<APIDeveloperAPIApiTokenScopeManagerCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("Token Scopes");
    expect(container.textContent).toContain("1 active tokens");
    expect(container.textContent).toContain("CI Token");
    expect(container.textContent).toContain("webhooks:read");
    expect(container.textContent).toContain("REVOKED");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiTokenScopeManagerCard tokens={[]} appName="App" />);
    expect(container.textContent).toContain("No tokens");
  });
});
