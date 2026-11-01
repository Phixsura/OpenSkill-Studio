import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-api-gateway-route-config-card";

describe("ApiGatewayRouteConfigCard", () => {
  it("shows routes", () => {
    const rules = [{ id: "r1", pattern: "/api/v1/users/*", methods: ["GET", "POST"], target: "user-svc", authRequired: true, timeoutMs: 30000 }];
    const { container } = render(<Card rules={rules} appName="App" />);
    expect(container.textContent).toContain("Gateway Routes");
    expect(container.textContent).toContain("/api/v1/users/*");
    expect(container.textContent).toContain("user-svc");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("Auth");
  });
  it("shows empty", () => {
    const { container } = render(<Card rules={[]} appName="App" />);
    expect(container.textContent).toContain("No routes configured");
  });
});
