import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatTrendPanel } from "@/components/lat-trend-panel";
describe("LatTrendPanel", () => {
  it("renders", () => {
    const { container } = render(<LatTrendPanel trend="worsening" changePct={50} recentP99={110} olderP99={55} />);
    expect(container.textContent).toContain("Latency Trend");
    expect(container.textContent).toContain("worsening");
    expect(container.textContent).toContain("+50%");
    expect(container.textContent).toContain("110ms");
  });
});
