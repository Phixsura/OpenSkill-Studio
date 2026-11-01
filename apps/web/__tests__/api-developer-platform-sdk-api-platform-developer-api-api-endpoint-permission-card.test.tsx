import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-endpoint-permission-card";

describe("EndpointPermissionCard", () => {
  it("shows rules", () => {
    const rules = [{ rule_id: "r1", endpoint: "/admin", method: "GET", public: false, scopes: ["admin"], roles: [] }];
    const { container } = render(<Card rules={rules} publicCount={0} appName="App" />);
    expect(container.textContent).toContain("Permissions");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/admin");
  });
  it("shows empty", () => {
    const { container } = render(<Card rules={[]} publicCount={0} appName="App" />);
    expect(container.textContent).toContain("No permission rules");
  });
});
