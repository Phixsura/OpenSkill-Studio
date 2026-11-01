import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RevenueDashboardView } from "@/components/revenue-dashboard-view";

describe("RevenueDashboardView", () => {
  const monthlyData = [
    { month: "2026-08", revenue: 5000, fees: 1500 },
    { month: "2026-09", revenue: 6000, fees: 1800 },
    { month: "2026-10", revenue: 7200, fees: 2160 },
  ];
  it("renders", () => {
    const { container } = render(
      <RevenueDashboardView totalRevenue={18200} netRevenue={12740} totalFees={5460}
        mrr={7200} arr={86400} avgMonthlyGrowth={20} monthlyData={monthlyData} />
    );
    expect(container.textContent).toContain("Revenue Dashboard");
    expect(container.textContent).toContain("$7,200");
    expect(container.textContent).toContain("$86,400");
    expect(container.textContent).toContain("+20%/mo");
    expect(container.textContent).toContain("2026-08");
    expect(container.textContent).toContain("2026-10");
  });
});
