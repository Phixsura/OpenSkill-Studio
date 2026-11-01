import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TokenExchangeCard from "../src/components/token-exchange-card";

const tokens = [
  {
    token_prefix: "sk_live",
    user_id: "user-1",
    scopes: ["read", "write"],
    issued_at: new Date(Date.now() - 3600_000).toISOString(),
    expires_at: new Date(Date.now() + 3600_000).toISOString(),
    revoked: false,
  },
  {
    token_prefix: "sk_test",
    user_id: "user-2",
    scopes: ["read"],
    issued_at: new Date(Date.now() - 86400_000).toISOString(),
    expires_at: new Date(Date.now() - 3600_000).toISOString(),
    revoked: false,
  },
  {
    token_prefix: "sk_old",
    user_id: "user-1",
    scopes: [],
    issued_at: new Date(Date.now() - 86400_000).toISOString(),
    expires_at: new Date(Date.now() + 86400_000).toISOString(),
    revoked: true,
  },
];

describe("TokenExchangeCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<TokenExchangeCard tokens={tokens} appName="My App" />);
    expect(container.textContent).toContain("Token Exchange");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(<TokenExchangeCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("1 active tokens");
  });

  it("renders token prefixes", () => {
    const { container } = render(<TokenExchangeCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("sk_live");
    expect(container.textContent).toContain("sk_test");
  });

  it("shows user ids", () => {
    const { container } = render(<TokenExchangeCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("user-1");
  });

  it("shows scopes", () => {
    const { container } = render(<TokenExchangeCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
  });

  it("shows revoked and expired labels", () => {
    const { container } = render(<TokenExchangeCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("revoked");
    expect(container.textContent).toContain("expired");
  });

  it("shows empty state", () => {
    const { container } = render(<TokenExchangeCard tokens={[]} appName="App" />);
    expect(container.textContent).toContain("No tokens issued");
  });
});
