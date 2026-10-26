import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthCheckWidget } from "@/components/health-check-widget";

const health = {
  status: "healthy" as const, version: "4.0.0", build: "4863", uptimeSeconds: 86400,
  components: {
    "API Gateway": { status: "healthy", latencyMs: 5, message: "" },
    "Database": { status: "healthy", latencyMs: 10, message: "" },
    "Cache": { status: "degraded", latencyMs: 500, message: "High latency" },
  },
};

describe("HealthCheckWidget", () => {
  it("renders health status", () => {
    const { container } = render(<HealthCheckWidget health={health} />);
    expect(container.textContent).toContain("All Systems Operational");
    expect(container.textContent).toContain("v4.0.0");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("High latency");
  });
});
