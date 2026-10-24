import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceKpiDashboard } from "@/components/marketplace-kpi-dashboard";

describe("MarketplaceKpiDashboard", () => {
  it("renders KPIs", () => {
    const kpis = [
      { label: "Apps", value: 500, icon: "📦", trend: "+10%" },
      { label: "Installs", value: 25000, icon: "📥" },
    ];
    const { container } = render(<MarketplaceKpiDashboard kpis={kpis} opportunities={["Reduce churn"]} />);
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("Reduce churn");
  });
});
