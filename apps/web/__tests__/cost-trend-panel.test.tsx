import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostTrendPanel } from "@/components/cost-trend-panel";
describe("CostTrendPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CostTrendPanel trend="increasing" changePct={20} current={1400}
        projectedNext={1447} totalSpend={4700} />
    );
    expect(container.textContent).toContain("Cost Trend");
    expect(container.textContent).toContain("increasing");
    expect(container.textContent).toContain("+20%");
    expect(container.textContent).toContain("$1,400");
    expect(container.textContent).toContain("$1,447");
    expect(container.textContent).toContain("$4,700");
  });
});
