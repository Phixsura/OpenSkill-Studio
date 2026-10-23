import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SliDashboard } from "@/components/sli-dashboard";

describe("SliDashboard", () => {
  it("renders SLIs", () => {
    const { container } = render(
      <SliDashboard allMeeting={false} avgRatio={99.5}
        slis={[
          { name: "Availability", ratioPct: 99.95, objectivePct: 99.9, meetingObjective: true, budgetConsumedPct: 50 },
          { name: "Latency", ratioPct: 99.0, objectivePct: 99.9, meetingObjective: false, budgetConsumedPct: 100 },
        ]} />
    );
    expect(container.textContent).toContain("Service Level Indicators");
    expect(container.textContent).toContain("avg 99.5%");
    expect(container.textContent).toContain("Objectives Missed");
    expect(container.textContent).toContain("Availability");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("Latency");
    expect(container.textContent).toContain("100% consumed");
  });
});
