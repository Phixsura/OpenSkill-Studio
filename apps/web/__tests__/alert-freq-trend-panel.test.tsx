import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlertFreqTrendPanel } from "@/components/alert-freq-trend-panel";
describe("AlertFreqTrendPanel", () => {
  it("renders", () => {
    const { container } = render(<AlertFreqTrendPanel trend="noisier" recentAvg={22.5} total={56} />);
    expect(container.textContent).toContain("Alert Frequency");
    expect(container.textContent).toContain("noisier");
    expect(container.textContent).toContain("56 total");
  });
});
