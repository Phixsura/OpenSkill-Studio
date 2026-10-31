import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MetricsExporterPanel } from "@/components/metrics-exporter-panel";

const mockMetrics = [
  { name: "http_requests_total", type: "counter" as const, value: 1500, labels: { method: "GET" } },
  { name: "cpu_usage", type: "gauge" as const, value: 42.5 },
  { name: "request_duration", type: "histogram" as const, value: 30,
    histogramStats: { count: 500, avg: 30, p50: 25, p99: 120 } },
];

describe("MetricsExporterPanel", () => {
  it("renders metrics with types", () => {
    const { container } = render(
      <MetricsExporterPanel metrics={mockMetrics} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("http_requests_total");
    expect(container.textContent).toContain("1500");
    expect(container.textContent).toContain("counter");
  });

  it("shows histogram stats", () => {
    const { container } = render(
      <MetricsExporterPanel metrics={mockMetrics} extensionName="Test" />
    );
    expect(container.textContent).toContain("p99: 120ms");
    expect(container.textContent).toContain("avg: 30ms");
  });

  it("filters by type", () => {
    const { getByText, container } = render(
      <MetricsExporterPanel metrics={mockMetrics} extensionName="Test" />
    );
    fireEvent.click(getByText("Gauges (1)"));
    expect(container.textContent).toContain("cpu_usage");
    expect(container.textContent).not.toContain("http_requests_total");
  });

  it("calls onExport", () => {
    const onExport = vi.fn();
    const { getByText } = render(
      <MetricsExporterPanel metrics={mockMetrics} extensionName="Test" onExport={onExport} />
    );
    fireEvent.click(getByText("Export"));
    expect(onExport).toHaveBeenCalled();
  });
});
