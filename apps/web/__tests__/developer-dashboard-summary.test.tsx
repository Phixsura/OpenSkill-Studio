import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperDashboardSummary } from "@/components/developer-dashboard-summary";

const props = {
  trends: [
    { metric: "installs", current: 1500, change: 50, trend: "up" as const },
    { metric: "revenue_cents", current: 50000, change: 25, trend: "up" as const },
  ],
  alerts: [{ severity: "warning", message: "Elevated error rate", action: "Monitor" }],
  healthScore: 95, totalInstalls: 1500, errorRate: 2.5, avgRating: 4.5,
};

describe("DeveloperDashboardSummary", () => {
  it("renders dashboard metrics", () => {
    const { container } = render(<DeveloperDashboardSummary {...props} />);
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("★ 4.5");
    expect(container.textContent).toContain("+50%");
  });

  it("shows alerts", () => {
    const { container } = render(<DeveloperDashboardSummary {...props} />);
    expect(container.textContent).toContain("Elevated error rate");
    expect(container.textContent).toContain("Monitor");
  });
});
