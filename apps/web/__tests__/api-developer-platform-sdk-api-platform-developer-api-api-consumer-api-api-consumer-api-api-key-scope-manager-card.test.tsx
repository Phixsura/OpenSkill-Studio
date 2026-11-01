import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-api-key-scope-manager-card";

describe("ApiKeyScopeManagerCard", () => {
  it("shows scopes", () => {
    const keys = [{ keyId: "k1", scopes: ["read:users", "write:orders"], denyScopes: ["delete:all"] }];
    const { container } = render(<Card keys={keys} appName="App" />);
    expect(container.textContent).toContain("Key Scopes");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("read:users");
    expect(container.textContent).toContain("delete:all");
  });
  it("shows empty", () => {
    const { container } = render(<Card keys={[]} appName="App" />);
    expect(container.textContent).toContain("No keys configured");
  });
});
