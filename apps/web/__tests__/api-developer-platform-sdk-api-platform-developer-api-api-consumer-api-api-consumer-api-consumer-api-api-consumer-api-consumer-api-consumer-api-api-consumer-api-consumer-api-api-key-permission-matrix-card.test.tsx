import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-api-consumer-api-consumer-api-api-key-permission-matrix-card";

describe("ApiKeyPermissionMatrixCard", () => {
  it("shows permissions", () => {
    const entries = [{ keyId: "k1", endpoint: "/api/users", method: "GET", allowed: true }, { keyId: "k1", endpoint: "/api/admin", method: "*", allowed: false }];
    const { container } = render(<Card entries={entries} keyId="k1" consumerId="c1" defaultAllow={false} appName="App" />);
    expect(container.textContent).toContain("Permission Matrix");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("✓ Allow");
    expect(container.textContent).toContain("✗ Deny");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} keyId="k1" consumerId="c1" defaultAllow={true} appName="App" />);
    expect(container.textContent).toContain("No explicit permissions");
  });
});
