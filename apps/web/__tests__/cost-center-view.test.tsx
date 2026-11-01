import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostCenterView } from "@/components/cost-center-view";

describe("CostCenterView", () => {
  it("renders costs", () => {
    const { container } = render(
      <CostCenterView dimension="team" total={1000} top="platform" trend="up" pctChange={25}
        allocations={{ platform: 800, data: 200 }} />
    );
    expect(container.textContent).toContain("Cost by team");
    expect(container.textContent).toContain("$1,000");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("$800");
  });
});
