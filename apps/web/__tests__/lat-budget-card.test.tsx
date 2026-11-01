import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatBudgetCard } from "@/components/lat-budget-card";

describe("LatBudgetCard", () => {
  it("renders", () => {
    const { container } = render(
      <LatBudgetCard endpoint="/api/users" totalBudgetMs={500} allocatedMs={300} overBudget={false}
        stages={[
          { stage: "auth", budgetMs: 50, actualMs: 30, withinBudget: true },
          { stage: "db_query", budgetMs: 200, actualMs: 150, withinBudget: true },
        ]} />
    );
    expect(container.textContent).toContain("Latency Budget");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("Within Budget");
    expect(container.textContent).toContain("300/500ms");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("30ms / 50ms");
  });
});
