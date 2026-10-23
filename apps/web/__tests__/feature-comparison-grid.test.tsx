import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureComparisonGrid } from "@/components/feature-comparison-grid";

describe("FeatureComparisonGrid", () => {
  const columns = [{ id: "a", name: "AppA", icon: "📦" }, { id: "b", name: "AppB", icon: "🚀" }];
  const rows = [
    { feature: "SSO", values: { a: { value: true, display: "✓", type: "bool" }, b: { value: false, display: "✗", type: "bool" } } },
  ];
  it("renders comparison grid", () => {
    const { container } = render(<FeatureComparisonGrid columns={columns} rows={rows} />);
    expect(container.textContent).toContain("AppA");
    expect(container.textContent).toContain("AppB");
    expect(container.textContent).toContain("SSO");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✗");
  });
});
