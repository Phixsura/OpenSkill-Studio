import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostPerReqPanel } from "@/components/cost-per-req-panel";
describe("CostPerReqPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CostPerReqPanel costPer1k={0.1} costPerMillion={100}
        endpoints={[
          { endpoint: "/users", requests: 7000, cost: 70, costPer1k: 10, sharePct: 70 },
          { endpoint: "/orders", requests: 3000, cost: 30, costPer1k: 10, sharePct: 30 },
        ]} />
    );
    expect(container.textContent).toContain("Cost per Request");
    expect(container.textContent).toContain("$0.1/1K reqs");
    expect(container.textContent).toContain("$100/M");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("$70");
    expect(container.textContent).toContain("70%");
  });
});
