import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsDashboardPage } from "@/components/analytics-dashboard-page";

describe("AnalyticsDashboardPage", () => {
  it("renders analytics", () => {
    const { container } = render(
      <AnalyticsDashboardPage dauDisplay="5,000" mauDisplay="20,000"
        dauMauRatio={25} engagement="high" apiDisplay="2,500,000"
        revenueDisplay="$125,000" newAppsMtd={45} avgSessionMin={12.5}
        npsScore={65} supportTicketsOpen={23}
        healthIndicators={[
          { metric: "NPS", status: "excellent", value: 65 },
          { metric: "Churn", status: "excellent", value: 1.8 },
        ]} />
    );
    expect(container.textContent).toContain("Platform Analytics");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("$125,000");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("high engagement");
    expect(container.textContent).toContain("NPS: 65");
    expect(container.textContent).toContain("23 open tickets");
  });
});
