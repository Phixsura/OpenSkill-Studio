import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-key-permission-matrix-card";

describe("KeyPermissionMatrixCard", () => {
  it("shows matrices", () => {
    const matrices = [{ key_id: "k1", consumer_id: "c1", permissions: [{ endpoint: "/users", method: "GET", allowed: true }], default_allow: false }];
    const { container } = render(<Card matrices={matrices} appName="App" />);
    expect(container.textContent).toContain("Key Permissions");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("deny default");
  });
  it("shows empty", () => {
    const { container } = render(<Card matrices={[]} appName="App" />);
    expect(container.textContent).toContain("No permission matrices");
  });
});
