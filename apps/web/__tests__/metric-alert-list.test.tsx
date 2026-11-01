import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricAlertList } from "@/components/metric-alert-list";

describe("MetricAlertList", () => {
  it("renders alerts", () => {
    const { container } = render(
      <MetricAlertList fired={1} allClear={false} results={[
        { name: "High CPU", metric: "cpu_pct", current: 95, threshold: 90, operator: ">", triggered: true, severity: "critical" },
        { name: "Memory", metric: "mem_pct", current: 60, threshold: 80, operator: ">", triggered: false, severity: null },
      ]} />
    );
    expect(container.textContent).toContain("Metric Alerts");
    expect(container.textContent).toContain("1 firing");
    expect(container.textContent).toContain("High CPU");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("Memory");
  });
});
