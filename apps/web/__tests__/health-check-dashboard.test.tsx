import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthCheckDashboard } from "@/components/health-check-dashboard";

describe("HealthCheckDashboard", () => {
  it("renders checks", () => {
    const { container } = render(
      <HealthCheckDashboard overall="degraded" healthPct={50}
        checks={[
          { service: "API", status: "healthy", latencyMs: 50, message: "" },
          { service: "Database", status: "unhealthy", latencyMs: 5000, message: "timeout" },
        ]} />
    );
    expect(container.textContent).toContain("System Health");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("timeout");
  });
});
