import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MetricsCollectorPanel } from "@/components/metrics-collector-panel";

const props = {
  currentValues: { cpu: 65, memory: 78, disk: 45 },
  aggregates: [
    { name: "cpu", count: 100, avg: 55, min: 10, max: 95, p95: 85 },
    { name: "latency", count: 500, avg: 42, min: 5, max: 500, p95: 150 },
  ],
  alerts: [
    { metric: "cpu", current: 95, threshold: 90, exceeded: true },
    { metric: "memory", current: 70, threshold: 85, exceeded: false },
  ],
  metricNames: ["cpu", "memory", "disk", "latency"],
};

describe("MetricsCollectorPanel", () => {
  it("renders current values", () => {
    const { container } = render(<MetricsCollectorPanel {...props} />);
    expect(container.textContent).toContain("65");
    expect(container.textContent).toContain("cpu");
    expect(container.textContent).toContain("1 alerts");
  });

  it("shows aggregates", () => {
    const { getByText, container } = render(<MetricsCollectorPanel {...props} />);
    fireEvent.click(getByText("Aggregates"));
    expect(container.textContent).toContain("avg: 55");
    expect(container.textContent).toContain("p95: 85");
  });

  it("shows alerts", () => {
    const { getByText, container } = render(<MetricsCollectorPanel {...props} />);
    fireEvent.click(getByText("Alerts (1)"));
    expect(container.textContent).toContain("95 / 90");
  });

  it("calls onRefresh", () => {
    const onRefresh = vi.fn();
    const { getByText } = render(<MetricsCollectorPanel {...props} onRefresh={onRefresh} />);
    fireEvent.click(getByText("Refresh"));
    expect(onRefresh).toHaveBeenCalled();
  });
});
