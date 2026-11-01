import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import OAuthScopeCard from "../src/components/api-developer-platform-sdk-consumer-api-oauth-scope-card";

describe("OAuthScopeCard", () => {
  it("renders title and scopes", () => {
    const { container } = render(<OAuthScopeCard />);
    expect(container.textContent).toContain("OAuth Scopes");
    expect(container.textContent).toContain("read:users");
    expect(container.textContent).toContain("admin");
  });

  it("shows sensitive and counts", () => {
    const { container } = render(<OAuthScopeCard />);
    expect(container.textContent).toContain("sensitive");
    expect(container.textContent).toContain("4 scopes");
    expect(container.textContent).toContain("2 sensitive");
  });
});
