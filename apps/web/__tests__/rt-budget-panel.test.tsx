import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RtBudgetPanel } from "@/components/rt-budget-panel";
describe("RtBudgetPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RtBudgetPanel endpoint="/api/users" budgetMs={200} usedMs={95} remainingMs={105}
        pctUsed={47.5} overBudget={false}
        stages={[
          { name: "auth", ms: 10, pct: 5 },
          { name: "query", ms: 80, pct: 40 },
          { name: "serialize", ms: 5, pct: 2.5 },
        ]} />
    );
    expect(container.textContent).toContain("RT Budget: /api/users");
    expect(container.textContent).toContain("95/200ms");
    expect(container.textContent).toContain("47.5%");
    expect(container.textContent).toContain("105ms left");
    expect(container.textContent).toContain("auth: 10ms");
    expect(container.textContent).toContain("query: 80ms");
  });
});
