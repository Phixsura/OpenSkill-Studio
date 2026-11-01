import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PerfBudgetCard from "../src/components/api-developer-platform-sdk-consumer-api-perf-budget-card";

describe("PerfBudgetCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<PerfBudgetCard />);
    expect(container.textContent).toContain("Performance Budget");
    expect(container.textContent).toContain("ep-auth");
    expect(container.textContent).toContain("ep-search");
  });

  it("shows budget status and violations", () => {
    const { container } = render(<PerfBudgetCard />);
    expect(container.textContent).toContain("2 violations");
    expect(container.textContent).toContain("2/3 within budget");
  });
});
