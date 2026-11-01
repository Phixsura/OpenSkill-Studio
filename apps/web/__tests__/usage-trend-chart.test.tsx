import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageTrendChart } from "@/components/usage-trend-chart";

describe("UsageTrendChart", () => {
  it("renders trend", () => {
    const { container } = render(
      <UsageTrendChart trend="growing" growthPct={25} recentAvg={30}
        olderAvg={24} peak={36} trough={10} points={14} />
    );
    expect(container.textContent).toContain("Usage Trend");
    expect(container.textContent).toContain("growing");
    expect(container.textContent).toContain("+25%");
    expect(container.textContent).toContain("30");
    expect(container.textContent).toContain("36");
  });
});
