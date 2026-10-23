import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GatewayRoutesTable } from "@/components/gateway-routes-table";

describe("GatewayRoutesTable", () => {
  it("renders routes", () => {
    const { container } = render(
      <GatewayRoutesTable total={2} rateLimited={1} routes={[
        { path: "/api/users", upstream: "user-svc:8080", methods: ["GET", "POST"], authRequired: true, rateLimit: 100 },
        { path: "/api/health", upstream: "health-svc:8080", methods: ["GET"], authRequired: false, rateLimit: 0 },
      ]} />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("2 routes");
    expect(container.textContent).toContain("1 rate-limited");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("public");
    expect(container.textContent).toContain("POST");
  });
});
