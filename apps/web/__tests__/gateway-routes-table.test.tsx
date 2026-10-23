import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GatewayRoutesTable } from "@/components/gateway-routes-table";

describe("GatewayRoutesTable", () => {
  it("renders routes", () => {
    const { container } = render(
      <GatewayRoutesTable middleware={["cors", "rate_limit"]} onToggle={vi.fn()}
        routes={[
          { path: "/api/v1/users", upstream: "http://users:8001", methods: ["GET"], rateLimit: 100, authRequired: true, enabled: true },
        ]} />
    );
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("1 routes");
    expect(container.textContent).toContain("2 middleware");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("http://users:8001");
  });
});
