import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppMetricsChart } from "@/components/app-metrics-chart";

const DATA = [
  { date: "2026-01", value: 100 },
  { date: "2026-02", value: 200 },
  { date: "2026-03", value: 150 },
];

describe("AppMetricsChart", () => {
  it("renders title", () => {
    const { container } = render(<AppMetricsChart title="API Calls" data={DATA} />);
    expect(container.textContent).toContain("API Calls");
  });

  it("shows total", () => {
    const { container } = render(<AppMetricsChart title="Calls" data={DATA} />);
    expect(container.textContent).toContain("450");
  });

  it("shows avg", () => {
    const { container } = render(<AppMetricsChart title="Calls" data={DATA} />);
    expect(container.textContent).toContain("150");
  });

  it("renders bars", () => {
    const { container } = render(<AppMetricsChart title="Calls" data={DATA} />);
    const bars = container.querySelectorAll("[style]");
    expect(bars.length).toBeGreaterThan(0);
  });

  it("empty state", () => {
    const { container } = render(<AppMetricsChart title="Calls" data={[]} />);
    expect(container.textContent).toContain("No data");
  });

  it("shows date range", () => {
    const { container } = render(<AppMetricsChart title="Calls" data={DATA} />);
    expect(container.textContent).toContain("2026-01");
    expect(container.textContent).toContain("2026-03");
  });
});
