import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MetricAlertCard from "../src/components/metric-alert-card";

const rules = [
  {
    rule_id: "r1",
    metric_name: "cpu_pct",
    operator: "gt",
    threshold: 80,
    severity: "critical",
    state: "firing" as const,
    fire_count: 3,
  },
  {
    rule_id: "r2",
    metric_name: "memory_mb",
    operator: "lt",
    threshold: 100,
    severity: "warning",
    state: "ok" as const,
    fire_count: 0,
  },
];

describe("MetricAlertCard", () => {
  it("renders header and firing count", () => {
    const { container } = render(<MetricAlertCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Metric Alerts");
    expect(container.textContent).toContain("1 firing");
  });

  it("shows metric conditions", () => {
    const { container } = render(<MetricAlertCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("cpu_pct > 80");
    expect(container.textContent).toContain("memory_mb < 100");
  });

  it("shows fire counts", () => {
    const { container } = render(<MetricAlertCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("3x fired");
  });

  it("shows empty state", () => {
    const { container } = render(<MetricAlertCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No alert rules");
  });
});
