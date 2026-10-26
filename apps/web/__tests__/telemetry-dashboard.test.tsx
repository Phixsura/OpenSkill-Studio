import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TelemetryDashboard } from "@/components/telemetry-dashboard";

const mockStats = {
  totalRecords: 5000, droppedBySampling: 500,
  exported: { prometheus: 4000, datadog: 3000 }, configuredExtensions: 5,
};
const mockAggregates = [
  { name: "request_latency", count: 1000, sum: 50000, avg: 50, min: 5, max: 500 },
];
const mockRecords = [
  { id: "t1", type: "metric" as const, name: "cpu", value: 65, tags: { host: "a" } },
  { id: "t2", type: "event" as const, name: "deploy", value: 1, tags: {} },
];

describe("TelemetryDashboard", () => {
  it("renders stats", () => {
    const { container } = render(
      <TelemetryDashboard stats={mockStats} aggregates={mockAggregates} recentRecords={mockRecords} />
    );
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("91%"); // accept rate
  });

  it("shows export targets", () => {
    const { container } = render(
      <TelemetryDashboard stats={mockStats} aggregates={mockAggregates} recentRecords={mockRecords} />
    );
    expect(container.textContent).toContain("prometheus");
    expect(container.textContent).toContain("4,000");
  });

  it("shows aggregates tab", () => {
    const { getByText, container } = render(
      <TelemetryDashboard stats={mockStats} aggregates={mockAggregates} recentRecords={mockRecords} />
    );
    fireEvent.click(getByText("Aggregates"));
    expect(container.textContent).toContain("request_latency");
    expect(container.textContent).toContain("avg: 50");
  });

  it("calls onFlush", () => {
    const onFlush = vi.fn();
    const { getByText } = render(
      <TelemetryDashboard stats={mockStats} aggregates={[]} recentRecords={[]} onFlush={onFlush} />
    );
    fireEvent.click(getByText("Flush"));
    expect(onFlush).toHaveBeenCalled();
  });
});
