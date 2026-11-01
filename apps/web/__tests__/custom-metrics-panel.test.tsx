import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CustomMetricsPanel } from "@/components/custom-metrics-panel";
describe("CustomMetricsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CustomMetricsPanel metrics={[
        { name: "order_value", unit: "USD", count: 1500 },
        { name: "latency_p99", unit: "ms", count: 10000 },
      ]} />
    );
    expect(container.textContent).toContain("Custom Metrics");
    expect(container.textContent).toContain("2 metrics");
    expect(container.textContent).toContain("order_value");
    expect(container.textContent).toContain("USD");
    expect(container.textContent).toContain("1,500 points");
  });
});
