import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthTrendChart2 } from "@/components/health-trend-chart2";

describe("HealthTrendChart2", () => {
  it("renders", () => {
    const { container } = render(
      <HealthTrendChart2 trend="improving" currentAvg={92} delta={5}
        latest={95} min={80} max={95} dataPoints={7} />
    );
    expect(container.textContent).toContain("Health Trend");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("+5");
    expect(container.textContent).toContain("92");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("80");
  });
});
