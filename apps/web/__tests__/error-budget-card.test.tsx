import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorBudgetCard } from "@/components/error-budget-card";

const HEALTHY = {
  app_id: "app-1",
  slo_target_pct: 99.9,
  actual_success_pct: 99.99,
  budget_total_minutes: 43.2,
  budget_consumed_minutes: 4.32,
  budget_remaining_minutes: 38.88,
  budget_remaining_pct: 90.0,
  burn_rate: 0.1,
  status: "healthy" as const,
  window_days: 30,
};

const EXHAUSTED = {
  ...HEALTHY,
  actual_success_pct: 95.0,
  budget_remaining_minutes: 0,
  budget_remaining_pct: 0,
  burn_rate: 50.0,
  status: "exhausted" as const,
};

const CRITICAL = {
  ...HEALTHY,
  budget_remaining_pct: 5.0,
  budget_remaining_minutes: 2.16,
  burn_rate: 0.95,
  status: "critical" as const,
};

describe("ErrorBudgetCard", () => {
  it("renders heading and app name", () => {
    const { container } = render(<ErrorBudgetCard snapshot={HEALTHY} appName="My App" />);
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("My App");
  });

  it("renders window days", () => {
    const { container } = render(<ErrorBudgetCard snapshot={HEALTHY} appName="App" />);
    expect(container.textContent).toContain("30-day");
  });

  it("renders budget remaining percentage", () => {
    const { container } = render(<ErrorBudgetCard snapshot={HEALTHY} appName="App" />);
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("remaining");
  });

  it("renders healthy status", () => {
    const { container } = render(<ErrorBudgetCard snapshot={HEALTHY} appName="App" />);
    expect(container.textContent).toContain("healthy");
  });

  it("renders exhausted status", () => {
    const { container } = render(<ErrorBudgetCard snapshot={EXHAUSTED} appName="App" />);
    expect(container.textContent).toContain("exhausted");
    expect(container.textContent).toContain("SLO breached");
  });

  it("renders critical status", () => {
    const { container } = render(<ErrorBudgetCard snapshot={CRITICAL} appName="App" />);
    expect(container.textContent).toContain("action needed");
  });

  it("renders SLO target", () => {
    const { container } = render(<ErrorBudgetCard snapshot={HEALTHY} appName="App" />);
    expect(container.textContent).toContain("99.9%");
  });

  it("renders actual success", () => {
    const { container } = render(<ErrorBudgetCard snapshot={HEALTHY} appName="App" />);
    expect(container.textContent).toContain("99.99%");
  });

  it("renders budget remaining minutes", () => {
    const { container } = render(<ErrorBudgetCard snapshot={HEALTHY} appName="App" />);
    expect(container.textContent).toContain("39 min");
  });

  it("renders burn rate", () => {
    const { container } = render(<ErrorBudgetCard snapshot={HEALTHY} appName="App" />);
    expect(container.textContent).toContain("0.10×");
  });

  it("renders high burn rate in red", () => {
    const { container } = render(<ErrorBudgetCard snapshot={EXHAUSTED} appName="App" />);
    expect(container.textContent).toContain("50.00×");
  });
});
