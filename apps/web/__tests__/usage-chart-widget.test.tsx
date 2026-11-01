import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageChartWidget } from "@/components/usage-chart-widget";

describe("UsageChartWidget", () => {
  it("renders chart", () => {
    const { container } = render(
      <UsageChartWidget labels={["Oct 1", "Oct 2"]} values={[1000, 1500]}
        metric="api_calls" total={2500} average={1250} peak={1500} trend="up" />
    );
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("2,500");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("Oct 1");
  });
});
