import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncCountTrendPanel } from "@/components/inc-count-trend-panel";
describe("IncCountTrendPanel", () => {
  it("renders", () => {
    const { container } = render(<IncCountTrendPanel trend="worsening" recentAvg={6.5} olderAvg={1.5} total={16} />);
    expect(container.textContent).toContain("Incident Trend");
    expect(container.textContent).toContain("worsening");
    expect(container.textContent).toContain("16 total");
    expect(container.textContent).toContain("6.5/period");
  });
});
