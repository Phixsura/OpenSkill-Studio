import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SLITrackerCard from "../src/components/sli-tracker-card";

const reports = [
  {
    metric: "availability",
    current: 99.95,
    average: 99.9,
    target: 99.9,
    meets_target: true,
    measurement_count: 100,
  },
  {
    metric: "latency_p99",
    current: 250,
    average: 180,
    target: 200,
    meets_target: false,
    measurement_count: 50,
  },
];

describe("SLITrackerCard", () => {
  it("renders header", () => {
    const { container } = render(<SLITrackerCard reports={reports} appName="My App" />);
    expect(container.textContent).toContain("SLI Tracker");
  });

  it("shows below-target count", () => {
    const { container } = render(<SLITrackerCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("1 below target");
  });

  it("shows all-on-target", () => {
    const { container } = render(<SLITrackerCard reports={[reports[0]]} appName="App" />);
    expect(container.textContent).toContain("All on target");
  });

  it("renders metrics with values", () => {
    const { container } = render(<SLITrackerCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("availability");
    expect(container.textContent).toContain("99.95");
    expect(container.textContent).toContain("target 99.9");
  });

  it("shows empty state", () => {
    const { container } = render(<SLITrackerCard reports={[]} appName="App" />);
    expect(container.textContent).toContain("No SLI data");
  });
});
