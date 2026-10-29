import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIAccessTokenManagerCard from "../src/components/api-developer-api-access-token-manager-card";

const tokens = [
  { token_id: "t1", name: "Prod Token", developer_id: "alice", scopes: ["read", "write"], is_active: true, use_count: 500, revoked: false },
  { token_id: "t2", name: "Old Token", developer_id: "alice", scopes: [], is_active: false, use_count: 100, revoked: true },
];

describe("APIDeveloperAPIAccessTokenManagerCard", () => {
  it("shows tokens", () => {
    const { container } = render(<APIDeveloperAPIAccessTokenManagerCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("Access Tokens");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("Prod Token");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("500 uses");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIAccessTokenManagerCard tokens={[]} appName="App" />);
    expect(container.textContent).toContain("No access tokens");
  });
});
