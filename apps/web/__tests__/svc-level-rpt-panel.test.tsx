import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcLevelRptPanel } from "@/components/svc-level-rpt-panel";
describe("SvcLevelRptPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SvcLevelRptPanel period="Q4 2026" compliancePct={66.7} sloMet={2} sloBreached={1}
        avgUptimePct={99.83} totalIncidents={4} totalDowntimeMin={221}
        executiveSummary="1 SLO breaches" />
    );
    expect(container.textContent).toContain("Service Level Report — Q4 2026");
    expect(container.textContent).toContain("1 SLO breaches");
    expect(container.textContent).toContain("66.7% compliance");
    expect(container.textContent).toContain("2");
    expect(container.textContent).toContain("99.83%");
    expect(container.textContent).toContain("221 minutes");
  });
});
