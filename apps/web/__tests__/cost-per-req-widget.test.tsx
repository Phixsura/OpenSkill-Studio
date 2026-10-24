import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostPerReqWidget } from "@/components/cost-per-req-widget";

describe("CostPerReqWidget", () => {
  it("renders", () => {
    const { container } = render(
      <CostPerReqWidget costPer1k={0.5} costPerMillion={500}
        totalCost={5000} totalRequests={10000000} improving={true} pctChange={-20} />
    );
    expect(container.textContent).toContain("Cost Per Request");
    expect(container.textContent).toContain("$0.5");
    expect(container.textContent).toContain("$500");
    expect(container.textContent).toContain("$5,000");
    expect(container.textContent).toContain("10.0M");
    expect(container.textContent).toContain("20%");
  });
});
