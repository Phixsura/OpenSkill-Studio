import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RevenueDashboardPage } from "@/components/revenue-dashboard-page";

describe("RevenueDashboardPage", () => {
  it("renders revenue", () => {
    const { container } = render(
      <RevenueDashboardPage mrrDisplay="$29,000.00" arrDisplay="$348,000.00"
        growthPct={16} growthTrend="up" subscribers={1000}
        arpuDisplay="$29.00" churnDisplay="2.5%"
        byPlan={[{ plan: "pro", revenue: 20000, display: "$20,000.00" }]} />
    );
    expect(container.textContent).toContain("Revenue");
    expect(container.textContent).toContain("$29,000.00");
    expect(container.textContent).toContain("$348,000.00");
    expect(container.textContent).toContain("16%");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("pro");
  });
});
