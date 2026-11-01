import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UserGrowthChart } from "@/components/user-growth-chart";

describe("UserGrowthChart", () => {
  const metrics = [
    { period: "2026-09", new_users: 600, churned: 40, net_growth: 560, total_users: 5560, growth_rate: 11.2 },
    { period: "2026-10", new_users: 700, churned: 30, net_growth: 670, total_users: 6230, growth_rate: 12.1 },
  ];
  it("renders", () => {
    const { container } = render(
      <UserGrowthChart metrics={metrics} currentTotal={6230} avgGrowthRate={11.6} trend="growing" />
    );
    expect(container.textContent).toContain("User Growth");
    expect(container.textContent).toContain("6,230");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("+11.6%");
    expect(container.textContent).toContain("+700");
    expect(container.textContent).toContain("-30");
  });
});
