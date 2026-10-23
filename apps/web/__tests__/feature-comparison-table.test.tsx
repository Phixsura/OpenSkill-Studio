import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureComparisonTable } from "@/components/feature-comparison-table";

describe("FeatureComparisonTable", () => {
  const matrix = [
    { id: "a2", name: "Pro", auth: true, api: true, analytics: true },
    { id: "a1", name: "Basic", auth: true, api: true, analytics: false },
  ];
  it("renders", () => {
    const { container } = render(
      <FeatureComparisonTable matrix={matrix} features={["auth", "api", "analytics"]} winnerId="a2" />
    );
    expect(container.textContent).toContain("Feature Comparison");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("🏆");
    expect(container.textContent).toContain("Basic");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("—");
  });
});
