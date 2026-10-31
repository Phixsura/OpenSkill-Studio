import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostTagView } from "@/components/cost-tag-view";

describe("CostTagView", () => {
  it("renders", () => {
    const { container } = render(
      <CostTagView totalCost={900} taggedPct={89} untaggedCost={100}
        byCostCenter={{ engineering: 800 }} />
    );
    expect(container.textContent).toContain("Cost Allocation");
    expect(container.textContent).toContain("$900");
    expect(container.textContent).toContain("89% tagged");
    expect(container.textContent).toContain("engineering");
    expect(container.textContent).toContain("$800");
    expect(container.textContent).toContain("Untagged");
  });
});
