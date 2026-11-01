import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcCostReportPanel } from "@/components/svc-cost-report-panel";
describe("SvcCostReportPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SvcCostReportPanel totalCost={1000}
        services={[
          { service: "api", cost: 500, sharePct: 50, team: "platform" },
          { service: "db", cost: 300, sharePct: 30, team: "data" },
        ]} />
    );
    expect(container.textContent).toContain("Service Costs");
    expect(container.textContent).toContain("$1,000/mo");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("$500");
    expect(container.textContent).toContain("50%");
  });
});
