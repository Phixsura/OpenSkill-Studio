import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageHeatmap } from "@/components/usage-heatmap";

const mockData = [
  { day: "Mon", hour: 9, value: 500 },
  { day: "Mon", hour: 10, value: 1200 },
  { day: "Mon", hour: 14, value: 800 },
  { day: "Tue", hour: 10, value: 1500 },
  { day: "Wed", hour: 15, value: 300 },
  { day: "Fri", hour: 16, value: 900 },
];

describe("UsageHeatmap", () => {
  it("renders metric name and total", () => {
    const { container } = render(<UsageHeatmap data={mockData} metricName="API Calls" />);
    expect(container.textContent).toContain("API Calls Heatmap");
    expect(container.textContent).toContain("5,200");
  });

  it("renders day labels", () => {
    const { container } = render(<UsageHeatmap data={mockData} metricName="Requests" />);
    expect(container.textContent).toContain("Mon");
    expect(container.textContent).toContain("Fri");
    expect(container.textContent).toContain("Sun");
  });

  it("shows peak info", () => {
    const { container } = render(<UsageHeatmap data={mockData} metricName="Calls" />);
    expect(container.textContent).toContain("Peak: Tue 10:00");
    expect(container.textContent).toContain("1,500");
  });

  it("renders legend", () => {
    const { container } = render(<UsageHeatmap data={mockData} metricName="Test" />);
    expect(container.textContent).toContain("Less");
    expect(container.textContent).toContain("More");
  });
});
