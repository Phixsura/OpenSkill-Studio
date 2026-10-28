import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CostTrackerCard from "../src/components/cost-tracker-card";

const breakdown = [
  { category: "compute", amount_cents: 5000 },
  { category: "storage", amount_cents: 2000 },
  { category: "network", amount_cents: 800 },
];

describe("CostTrackerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <CostTrackerCard totalDollars={78} breakdown={breakdown} appName="My App" />,
    );
    expect(container.textContent).toContain("Cost Tracker");
    expect(container.textContent).toContain("My App");
  });

  it("shows total dollars", () => {
    const { container } = render(
      <CostTrackerCard totalDollars={78} breakdown={breakdown} appName="App" />,
    );
    expect(container.textContent).toContain("$78.00");
  });

  it("renders category names", () => {
    const { container } = render(
      <CostTrackerCard totalDollars={78} breakdown={breakdown} appName="App" />,
    );
    expect(container.textContent).toContain("compute");
    expect(container.textContent).toContain("storage");
    expect(container.textContent).toContain("network");
  });

  it("shows category amounts", () => {
    const { container } = render(
      <CostTrackerCard totalDollars={78} breakdown={breakdown} appName="App" />,
    );
    expect(container.textContent).toContain("$50.00");
    expect(container.textContent).toContain("$20.00");
    expect(container.textContent).toContain("$8.00");
  });

  it("shows empty state", () => {
    const { container } = render(<CostTrackerCard totalDollars={0} breakdown={[]} appName="App" />);
    expect(container.textContent).toContain("No costs recorded");
  });
});
