import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerfBudgetCard } from "@/components/perf-budget-card";

describe("PerfBudgetCard", () => {
  it("renders budget", () => {
    const { container } = render(
      <PerfBudgetCard name="Web Vitals" violations={1} withinBudget={false} trend="improving"
        results={[
          { metric: "lcp_ms", limit: 2500, actual: 2200, over: false, pctOfBudget: 88 },
          { metric: "fid_ms", limit: 100, actual: 150, over: true, pctOfBudget: 150 },
        ]} />
    );
    expect(container.textContent).toContain("Web Vitals");
    expect(container.textContent).toContain("1 over");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("lcp_ms");
    expect(container.textContent).toContain("2200");
    expect(container.textContent).toContain("fid_ms");
  });
});
