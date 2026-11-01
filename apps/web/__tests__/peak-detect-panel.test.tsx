import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PeakDetectPanel } from "@/components/peak-detect-panel";
describe("PeakDetectPanel", () => {
  it("renders", () => {
    const { container } = render(
      <PeakDetectPanel avgRps={100} maxRps={600} totalHours={24}
        peaks={[
          { hour: 14, rps: 500, aboveAvgPct: 400 },
          { hour: 15, rps: 600, aboveAvgPct: 500 },
        ]} />
    );
    expect(container.textContent).toContain("Traffic Peaks");
    expect(container.textContent).toContain("2 peaks");
    expect(container.textContent).toContain("avg 100 rps");
    expect(container.textContent).toContain("max 600 rps");
    expect(container.textContent).toContain("Hour 14:00");
    expect(container.textContent).toContain("+400%");
  });
});
