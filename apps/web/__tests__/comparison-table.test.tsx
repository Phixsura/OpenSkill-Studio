import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ComparisonTable } from "@/components/comparison-table";

describe("ComparisonTable", () => {
  const plans = [{ id: "free", name: "Free", price: "$0", recommended: false }, { id: "pro", name: "Pro", price: "$29", recommended: true }];
  const features = [
    { feature: "API Access", category: "Core", values: { free: { type: "bool", value: true, display: "✓" }, pro: { type: "bool", value: true, display: "✓" } } },
    { feature: "Support", category: "Core", values: { free: { type: "text", value: "Email", display: "Email" }, pro: { type: "text", value: "Priority", display: "Priority" } } },
  ];
  it("renders plans and features", () => {
    const { container } = render(<ComparisonTable plans={plans} features={features} />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("API Access");
    expect(container.textContent).toContain("Recommended");
    expect(container.textContent).toContain("Priority");
  });
});
