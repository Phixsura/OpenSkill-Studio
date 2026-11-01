import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiHealthMonitorPanel } from "@/components/api-health-monitor-panel";

const eps = [
  { endpoint: "/api/users", availability: 99.95, avgLatency: 45, sloTarget: 99.9, sloMet: true, errorBudgetRemaining: 5, totalRequests: 10000 },
  { endpoint: "/api/data", availability: 98.5, avgLatency: 200, sloTarget: 99.9, sloMet: false, errorBudgetRemaining: 0, totalRequests: 5000 },
];

describe("ApiHealthMonitorPanel", () => {
  it("renders endpoints with SLO status", () => {
    const { container } = render(<ApiHealthMonitorPanel endpoints={eps} />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("1 SLO violations");
  });
});
