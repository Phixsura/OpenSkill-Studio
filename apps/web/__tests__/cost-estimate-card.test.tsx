import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostEstimateCard } from "@/components/cost-estimate-card";

const MOCK_ESTIMATE = {
  app_id: "app-1",
  line_items: [
    {
      category: "api_calls",
      projected_usage: 100000,
      included: 50000,
      overage: 50000,
      unit_price: 0.001,
      cost: 50.0,
    },
    {
      category: "storage",
      projected_usage: 40,
      included: 5,
      overage: 35,
      unit_price: 0.05,
      cost: 1.75,
    },
    {
      category: "bandwidth",
      projected_usage: 8,
      included: 10,
      overage: 0,
      unit_price: 0.1,
      cost: 0,
    },
  ],
  total_cost: 51.75,
  budget_limit: 100.0,
  over_budget: false,
  savings_vs_next_tier: 25.5,
};

const OVER_BUDGET = { ...MOCK_ESTIMATE, total_cost: 150.0, over_budget: true, budget_limit: 100.0 };
const EMPTY = { ...MOCK_ESTIMATE, line_items: [], total_cost: 0, savings_vs_next_tier: null };

describe("CostEstimateCard", () => {
  it("renders heading and app name", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="My App" />);
    expect(container.textContent).toContain("Cost Estimate");
    expect(container.textContent).toContain("My App");
  });

  it("renders total cost", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="App" />);
    expect(container.textContent).toContain("$51.75");
  });

  it("renders category labels", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="App" />);
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("Storage");
    expect(container.textContent).toContain("Bandwidth");
  });

  it("renders per-item costs", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="App" />);
    expect(container.textContent).toContain("$50.00");
    expect(container.textContent).toContain("$1.75");
  });

  it("renders overage amounts", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="App" />);
    expect(container.textContent).toContain("50.0K overage");
  });

  it("renders projected and included", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="App" />);
    expect(container.textContent).toContain("100.0K projected");
    expect(container.textContent).toContain("50.0K included");
  });

  it("shows over budget banner", () => {
    const { container } = render(<CostEstimateCard estimate={OVER_BUDGET} appName="App" />);
    expect(container.textContent).toContain("Over budget");
    expect(container.textContent).toContain("$100.00");
  });

  it("hides budget banner when under", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="App" />);
    expect(container.textContent).not.toContain("Over budget");
  });

  it("shows savings tip", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="App" />);
    expect(container.textContent).toContain("Save $25.50");
    expect(container.textContent).toContain("Growth");
  });

  it("hides savings when null", () => {
    const { container } = render(<CostEstimateCard estimate={EMPTY} appName="App" />);
    expect(container.textContent).not.toContain("Save");
  });

  it("shows empty state", () => {
    const { container } = render(<CostEstimateCard estimate={EMPTY} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });

  it("renders category icons", () => {
    const { container } = render(<CostEstimateCard estimate={MOCK_ESTIMATE} appName="App" />);
    expect(container.textContent).toContain("📡");
    expect(container.textContent).toContain("💾");
  });
});
