import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-key-scope-card";

describe("ApiKeyScopeCard", () => {
  it("shows keys and scopes", () => {
    const keys = [{ key_id: "k1", scopes: ["read", "write"], read_only: false, description: "Main key" }];
    const { container } = render(<Card keys={keys} appName="App" />);
    expect(container.textContent).toContain("API Key Scopes");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
  });
  it("shows read-only badge", () => {
    const keys = [{ key_id: "k2", scopes: ["read"], read_only: true, description: "" }];
    const { container } = render(<Card keys={keys} appName="App" />);
    expect(container.textContent).toContain("READ-ONLY");
  });
});
