import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostSvcTrendPanel } from "@/components/cost-svc-trend-panel";
describe("CostSvcTrendPanel", () => {
  it("renders", () => {
    const { container } = render(<CostSvcTrendPanel trend="increasing" changePct={100} current={200} />);
    expect(container.textContent).toContain("Cost Trend");
    expect(container.textContent).toContain("+100%");
  });
});
