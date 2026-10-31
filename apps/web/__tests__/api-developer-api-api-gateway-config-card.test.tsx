import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiGatewayConfigCard from "../src/components/api-developer-api-api-gateway-config-card";

const routes = [
  { route_id: "r1", path_pattern: "/api/users*", upstream: "http://users:8080", methods: ["GET", "POST"], rate_limit: 100, auth_required: true, enabled: true, timeout_ms: 30000 },
  { route_id: "r2", path_pattern: "/api/health", upstream: "http://health:8080", methods: ["GET"], rate_limit: null, auth_required: false, enabled: false, timeout_ms: 5000 },
];

describe("APIDeveloperAPIApiGatewayConfigCard", () => {
  it("shows routes", () => {
    const { container } = render(<APIDeveloperAPIApiGatewayConfigCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("1/2 enabled");
    expect(container.textContent).toContain("/api/users*");
    expect(container.textContent).toContain("http://users:8080");
    expect(container.textContent).toContain("100 rpm");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiGatewayConfigCard routes={[]} appName="App" />);
    expect(container.textContent).toContain("No gateway routes");
  });
});
