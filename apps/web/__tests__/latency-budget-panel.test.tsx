import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatencyBudgetPanel } from "@/components/latency-budget-panel";
describe("LatencyBudgetPanel", () => {
  it("renders", () => {
    const { container } = render(
      <LatencyBudgetPanel totalMs={200} remainingMs={30}
        stages={[
          { stage: "auth", budgetMs: 20, pct: 10 },
          { stage: "logic", budgetMs: 100, pct: 50 },
          { stage: "db", budgetMs: 50, pct: 25 },
        ]} />
    );
    expect(container.textContent).toContain("Latency Budget");
    expect(container.textContent).toContain("200ms total");
    expect(container.textContent).toContain("30ms remaining");
    expect(container.textContent).toContain("auth: 20ms");
    expect(container.textContent).toContain("logic: 100ms");
  });
});
