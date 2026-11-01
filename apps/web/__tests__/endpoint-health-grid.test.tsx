import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EndpointHealthGrid } from "@/components/endpoint-health-grid";

describe("EndpointHealthGrid", () => {
  it("renders grid", () => {
    const { container } = render(
      <EndpointHealthGrid healthPct={67} healthy={2} degraded={1} unhealthy={0}
        endpoints={[
          { path: "/users", method: "GET", p99Ms: 100, errorRate: 0.1, rpm: 1000, status: "healthy" },
          { path: "/orders", method: "POST", p99Ms: 400, errorRate: 0.5, rpm: 200, status: "healthy" },
          { path: "/legacy", method: "GET", p99Ms: 800, errorRate: 3, rpm: 50, status: "degraded" },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint Health");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("100ms");
    expect(container.textContent).toContain("/legacy");
  });
});
