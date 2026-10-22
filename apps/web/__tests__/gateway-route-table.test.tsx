import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GatewayRouteTable } from "@/components/gateway-route-table";

describe("GatewayRouteTable", () => {
  it("renders routes", () => {
    const routes = [{ path_pattern: "/api/v1/users", target_app_id: "a1", methods: ["GET", "POST"], auth_required: true, rate_limit: 100 }];
    const { container } = render(<GatewayRouteTable routes={routes} />);
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("100/min");
  });
  it("empty state", () => {
    const { container } = render(<GatewayRouteTable routes={[]} />);
    expect(container.textContent).toContain("No routes");
  });
});
