import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageForecastChart } from "@/components/usage-forecast-chart";

const mockData = [
  { period: "Oct 20", actual: 1000, confidence: 100 },
  { period: "Oct 21", actual: 1200, confidence: 100 },
  { period: "Oct 22", actual: 1100, confidence: 100 },
  { period: "Oct 23", actual: 1400, confidence: 100 },
  { period: "Oct 24", predicted: 1500, confidence: 90 },
  { period: "Oct 25", predicted: 1600, confidence: 80 },
  { period: "Oct 26", predicted: 1700, confidence: 70 },
];

describe("UsageForecastChart", () => {
  it("renders metric name and trend", () => {
    const { container } = render(
      <UsageForecastChart data={mockData} metricName="API Calls" unit="calls/day"
        trend="growing" growthRate={15.5} />
    );
    expect(container.textContent).toContain("API Calls Forecast");
    expect(container.textContent).toContain("Growing");
    expect(container.textContent).toContain("+15.5%");
  });

  it("renders all data points", () => {
    const { container } = render(
      <UsageForecastChart data={mockData} metricName="API" unit="calls"
        trend="growing" growthRate={10} />
    );
    expect(container.textContent).toContain("Oct 20");
    expect(container.textContent).toContain("Oct 26");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("1,700");
  });

  it("shows legend", () => {
    const { container } = render(
      <UsageForecastChart data={mockData} metricName="CPU" unit="minutes"
        trend="stable" growthRate={0} />
    );
    expect(container.textContent).toContain("Actual");
    expect(container.textContent).toContain("Forecast");
    expect(container.textContent).toContain("Unit: minutes");
  });

  it("shows declining trend", () => {
    const { container } = render(
      <UsageForecastChart data={mockData} metricName="Storage" unit="MB"
        trend="declining" growthRate={-8.2} />
    );
    expect(container.textContent).toContain("Declining");
    expect(container.textContent).toContain("-8.2%");
  });
});
