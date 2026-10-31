import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperTokenCard from "../src/components/api-developer-token-card";

const tokens = [
  { token_id: "t1", name: "My Token", prefix: "abc12345", scopes: ["read", "write"], revoked: false },
  { token_id: "t2", name: "Old Token", prefix: "xyz98765", scopes: [], revoked: true },
];

describe("APIDeveloperTokenCard", () => {
  it("shows tokens", () => {
    const { container } = render(<APIDeveloperTokenCard tokens={tokens} appName="App" />);
    expect(container.textContent).toContain("Developer Tokens");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("abc12345...");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("revoked");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperTokenCard tokens={[]} appName="App" />);
    expect(container.textContent).toContain("No tokens");
  });
});
