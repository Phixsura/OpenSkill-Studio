import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CostTrackerCard from "../src/components/cost-tracker-card";

const categories = [
  { category: "compute", amount: 85.0 },
  { category: "storage", amount: 15.0 },
];

const alerts = [{ category: "compute", spent: 85, limit: 100, pct: 85 }];

describe("CostTrackerCard", () => {
  it("renders header and total", () => {
    const { container } = render(
      <CostTrackerCard
        categories={categories}
        alerts={[]}
        totalSpent={100}
        currency="USD"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Cost Tracker");
    expect(container.textContent).toContain("USD 100.00");
  });

  it("shows categories with percentages", () => {
    const { container } = render(
      <CostTrackerCard
        categories={categories}
        alerts={[]}
        totalSpent={100}
        currency="USD"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("compute");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("storage");
  });

  it("shows budget alerts", () => {
    const { container } = render(
      <CostTrackerCard
        categories={categories}
        alerts={alerts}
        totalSpent={100}
        currency="USD"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("85% of budget");
  });

  it("shows amounts", () => {
    const { container } = render(
      <CostTrackerCard
        categories={categories}
        alerts={[]}
        totalSpent={100}
        currency="USD"
        appName="App"
      />,
    );
    expect(container.textContent).toContain("USD 85.00");
    expect(container.textContent).toContain("USD 15.00");
  });

  it("shows empty state", () => {
    const { container } = render(
      <CostTrackerCard categories={[]} alerts={[]} totalSpent={0} currency="USD" appName="App" />,
    );
    expect(container.textContent).toContain("No costs recorded");
  });
});
