import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureComparisonTable } from "@/components/feature-comparison-table";

describe("FeatureComparisonTable", () => {
  it("renders comparison", () => {
    const { container } = render(
      <FeatureComparisonTable products={["Basic", "Pro"]} bestMatch="Pro"
        scores={{ Basic: { total: 2, pct: 50 }, Pro: { total: 4, pct: 100 } }}
        matrix={[
          { feature: "sso", values: { Basic: false, Pro: true } },
          { feature: "api", values: { Basic: true, Pro: true } },
        ]} />
    );
    expect(container.textContent).toContain("Feature Comparison");
    expect(container.textContent).toContain("Basic");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("Best");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("100%");
  });
});
