import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TagCostBreakdown } from "@/components/tag-cost-breakdown";

describe("TagCostBreakdown", () => {
  it("renders breakdown", () => {
    const { container } = render(
      <TagCostBreakdown tagKey="team" totalDisplay="$1,000.00" coveragePct={90}
        untaggedCost={100} breakdown={[
          { tag: "data", cost: 500, resources: 1, pct: 50, display: "$500.00" },
          { tag: "platform", cost: 400, resources: 2, pct: 40, display: "$400.00" },
        ]} />
    );
    expect(container.textContent).toContain("Cost by team");
    expect(container.textContent).toContain("$1,000.00");
    expect(container.textContent).toContain("90% tagged");
    expect(container.textContent).toContain("data");
    expect(container.textContent).toContain("$500.00");
    expect(container.textContent).toContain("50%");
  });
});
