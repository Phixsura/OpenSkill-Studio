import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CustomMetricsPanel } from "@/components/custom-metrics-panel";

describe("CustomMetricsPanel", () => {
  it("renders metrics", () => {
    const { container } = render(
      <CustomMetricsPanel metrics={[
        { name: "orders_total", type: "counter", current: 1234, unit: "count", dataPoints: 50 },
        { name: "cpu_temp", type: "gauge", current: 72, unit: "°C", dataPoints: 100 },
      ]} />
    );
    expect(container.textContent).toContain("Custom Metrics");
    expect(container.textContent).toContain("orders_total");
    expect(container.textContent).toContain("1,234");
    expect(container.textContent).toContain("counter");
    expect(container.textContent).toContain("cpu_temp");
    expect(container.textContent).toContain("72");
  });
});
