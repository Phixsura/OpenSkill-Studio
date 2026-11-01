import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-access-token-manager-card";

describe("AccessTokenManagerCard", () => {
  it("shows tokens", () => {
    const tokens = [{ token_id: "at-1", consumer_id: "c1", scopes: ["read", "write"], expires_in_min: 45, revoked: false }];
    const { container } = render(<Card tokens={tokens} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Access Tokens");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("45m left");
    expect(container.textContent).toContain("read");
  });
  it("shows empty", () => {
    const { container } = render(<Card tokens={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No tokens issued");
  });
});
