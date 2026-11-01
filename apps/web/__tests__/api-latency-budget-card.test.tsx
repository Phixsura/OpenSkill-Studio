import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APILatencyBudgetCard from "../src/components/api-latency-budget-card";

const budgets = [
  {
    endpoint: "/api/users",
    p50: 45,
    p50_target_ms: 50,
    p95: 180,
    p95_target_ms: 200,
    p99: 450,
    p99_target_ms: 500,
    violations: [],
  },
  {
    endpoint: "/api/search",
    p50: 60,
    p50_target_ms: 50,
    p95: 250,
    p95_target_ms: 200,
    p99: 300,
    p99_target_ms: 500,
    violations: ["p50", "p95"],
  },
];

describe("APILatencyBudgetCard", () => {
  it("renders header and violation count", () => {
    const { container } = render(<APILatencyBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("Latency Budgets");
    expect(container.textContent).toContain("1 violating");
  });

  it("shows endpoints and percentiles", () => {
    const { container } = render(<APILatencyBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("p50: 45ms");
    expect(container.textContent).toContain("p95: 180ms");
  });

  it("shows violations", () => {
    const { container } = render(<APILatencyBudgetCard budgets={budgets} appName="App" />);
    expect(container.textContent).toContain("p50, p95");
  });

  it("shows empty state", () => {
    const { container } = render(<APILatencyBudgetCard budgets={[]} appName="App" />);
    expect(container.textContent).toContain("No latency budgets");
  });
});
