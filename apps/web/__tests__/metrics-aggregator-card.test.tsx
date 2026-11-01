import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MetricsAggregatorCard from "../src/components/metrics-aggregator-card";

const latencyMetric = {
  metric: "response_latency_ms",
  sum: 45000,
  avg: 45,
  min: 5,
  max: 250,
  count: 1000,
  p99: 210,
};

const requestMetric = {
  metric: "total_requests",
  sum: 50000,
  avg: 50,
  min: 10,
  max: 200,
  count: 1000,
  p99: 180,
};

describe("MetricsAggregatorCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <MetricsAggregatorCard metrics={[latencyMetric]} appName="My App" />,
    );
    expect(container.textContent).toContain("Metrics");
    expect(container.textContent).toContain("My App");
  });

  it("shows metric count and total points", () => {
    const { container } = render(
      <MetricsAggregatorCard metrics={[latencyMetric, requestMetric]} appName="App" />,
    );
    expect(container.textContent).toContain("2 metrics");
    expect(container.textContent).toContain("2.0K points");
  });

  it("renders metric name", () => {
    const { container } = render(<MetricsAggregatorCard metrics={[latencyMetric]} appName="App" />);
    expect(container.textContent).toContain("response_latency_ms");
  });

  it("shows aggregation values", () => {
    const { container } = render(<MetricsAggregatorCard metrics={[latencyMetric]} appName="App" />);
    expect(container.textContent).toContain("45"); // avg
    expect(container.textContent).toContain("5"); // min
    expect(container.textContent).toContain("250"); // max
    expect(container.textContent).toContain("45.0K"); // sum
    expect(container.textContent).toContain("210"); // p99
  });

  it("shows stat labels", () => {
    const { container } = render(<MetricsAggregatorCard metrics={[latencyMetric]} appName="App" />);
    expect(container.textContent).toContain("avg");
    expect(container.textContent).toContain("min");
    expect(container.textContent).toContain("max");
    expect(container.textContent).toContain("sum");
    expect(container.textContent).toContain("p99");
  });

  it("shows point count per metric", () => {
    const { container } = render(<MetricsAggregatorCard metrics={[latencyMetric]} appName="App" />);
    expect(container.textContent).toContain("1.0K pts");
  });

  it("shows empty state", () => {
    const { container } = render(<MetricsAggregatorCard metrics={[]} appName="App" />);
    expect(container.textContent).toContain("No metrics collected");
  });

  it("singular metric label", () => {
    const { container } = render(<MetricsAggregatorCard metrics={[latencyMetric]} appName="App" />);
    expect(container.textContent).toContain("1 metric");
    expect(container.textContent).not.toContain("1 metrics");
  });
});
