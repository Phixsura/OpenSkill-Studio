import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsPage } from "@/components/analytics-page";

describe("AnalyticsPage", () => {
  it("renders analytics", () => {
    const { container } = render(
      <AnalyticsPage appName="SuperApp" period="30d"
        kpis={[{ label: "Installs", display: "35", icon: "📥" }]}
        installChart={[{ date: "Jan 1", count: 10 }, { date: "Jan 2", count: 25 }]}
        topCountries={[{ country: "US", count: 20 }]} />
    );
    expect(container.textContent).toContain("SuperApp Analytics");
    expect(container.textContent).toContain("35");
    expect(container.textContent).toContain("US");
    expect(container.textContent).toContain("30d");
  });
});
