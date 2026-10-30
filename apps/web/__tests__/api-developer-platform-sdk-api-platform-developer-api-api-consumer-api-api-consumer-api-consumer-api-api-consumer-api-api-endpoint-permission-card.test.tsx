import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-endpoint-permission-card";

describe("ConsumerApiEndpointPermissionCard", () => {
  it("shows permissions", () => {
    const perms = [{ id: "p1", endpoint: "/api/users", method: "GET", allowed: true, rateLimit: 100 }];
    const { container } = render(<Card permissions={perms} consumerId="c1" defaultAllowed={false} appName="App" />);
    expect(container.textContent).toContain("Endpoint Permissions");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("Default: Deny");
  });
  it("shows empty", () => {
    const { container } = render(<Card permissions={[]} consumerId="c1" defaultAllowed={true} appName="App" />);
    expect(container.textContent).toContain("No explicit permissions");
  });
});
