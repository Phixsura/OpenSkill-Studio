import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SliDashboard } from "@/components/sli-dashboard";

describe("SliDashboard", () => {
  it("renders SLIs", () => {
    const { container } = render(
      <SliDashboard compositeDisplay="99.475%" allMet={false} slis={[
        { metric: "availability", sli: 99.95, sliDisplay: "99.950%", sloTarget: 99.9, met: true, errorBudgetPct: 50, status: "met" },
        { metric: "latency", sli: 99.0, sliDisplay: "99.000%", sloTarget: 99.9, met: false, errorBudgetPct: 1000, status: "breached" },
      ]} />
    );
    expect(container.textContent).toContain("Service Level Indicators");
    expect(container.textContent).toContain("99.475%");
    expect(container.textContent).toContain("SLO breach");
    expect(container.textContent).toContain("availability");
    expect(container.textContent).toContain("99.950%");
    expect(container.textContent).toContain("latency");
  });
});
