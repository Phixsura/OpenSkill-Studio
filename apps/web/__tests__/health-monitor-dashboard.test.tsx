import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthMonitorDashboard } from "@/components/health-monitor-dashboard";

describe("HealthMonitorDashboard", () => {
  const apps = [
    { name: "API", icon: "⚙️", status: "healthy", uptimePct: 99.99, responseMs: 45, errorRatePct: 0 },
    { name: "Web", icon: "🌐", status: "degraded", uptimePct: 99.5, responseMs: 200, errorRatePct: 2.5 },
  ];
  it("renders health monitor", () => {
    const { container } = render(
      <HealthMonitorDashboard apps={apps} overall="degraded" healthy={1} degraded={1} down={0} />
    );
    expect(container.textContent).toContain("Partial Degradation");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("2.5% err");
  });
});
