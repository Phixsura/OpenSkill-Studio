import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EndpointHealthTable } from "@/components/endpoint-health-table";

describe("EndpointHealthTable", () => {
  it("renders endpoints", () => {
    const { container } = render(
      <EndpointHealthTable overall="degraded" healthPct={67} avgLatencyMs={1055}
        results={[
          { path: "/api/v1/billing", method: "POST", statusCode: 500, latencyMs: 3000, healthy: false },
          { path: "/api/v1/apps", method: "GET", statusCode: 200, latencyMs: 120, healthy: true },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint Health");
    expect(container.textContent).toContain("67% healthy");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("/api/v1/billing");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("3000ms");
  });
});
