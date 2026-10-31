import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthDashboardGrid } from "@/components/health-dashboard-grid";

describe("HealthDashboardGrid", () => {
  const components = [
    { name: "API", type: "api", status: "healthy", latency_ms: 50, error_rate: 0.1, uptime_pct: 99.99 },
    { name: "Cache", type: "cache", status: "degraded", latency_ms: 500, error_rate: 3, uptime_pct: 99.5 },
  ];
  it("renders", () => {
    const { container } = render(<HealthDashboardGrid components={components} overall="degraded" />);
    expect(container.textContent).toContain("System Health");
    expect(container.textContent).toContain("🟡");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("🟢");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("Cache");
  });
});
