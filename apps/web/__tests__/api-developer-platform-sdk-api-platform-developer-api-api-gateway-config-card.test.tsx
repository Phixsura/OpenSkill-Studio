import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-gateway-config-card";

describe("GatewayConfigCard", () => {
  it("shows routes", () => {
    const routes = [{ route_id: "r1", path_pattern: "/api/v1/*", upstream: "http://svc", methods: ["GET"], middlewares: ["auth", "cors"], enabled: true }];
    const { container } = render(<Card routes={routes} appName="App" />);
    expect(container.textContent).toContain("Gateway Config");
    expect(container.textContent).toContain("/api/v1/*");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("cors");
  });
  it("shows empty", () => {
    const { container } = render(<Card routes={[]} appName="App" />);
    expect(container.textContent).toContain("No routes configured");
  });
});
