import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostAllocDash } from "@/components/cost-alloc-dash";

describe("CostAllocDash", () => {
  it("renders", () => {
    const { container } = render(
      <CostAllocDash totalCost={1000} budget={900} actual={1000} variancePct={11.1} status="over"
        byTeam={[
          { team: "platform", cost: 800, pct: 80 },
          { team: "data", cost: 200, pct: 20 },
        ]} />
    );
    expect(container.textContent).toContain("Cost Allocation");
    expect(container.textContent).toContain("$1,000/mo");
    expect(container.textContent).toContain("+11.1% vs budget");
    expect(container.textContent).toContain("$900");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("80%");
  });
});
