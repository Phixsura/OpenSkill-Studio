import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingComparisonTable } from "@/components/pricing-comparison-table";

describe("PricingComparisonTable", () => {
  const plans = [{ id: "free", name: "Free", priceDisplay: "Free", recommended: false },
                  { id: "pro", name: "Pro", priceDisplay: "$29/mo", recommended: true }];
  const features = [{ name: "Apps", values: {
    free: { display: "5", type: "text", value: "5" },
    pro: { display: "Unlimited", type: "text", value: "Unlimited" }}}];
  it("renders comparison", () => {
    const { container } = render(
      <PricingComparisonTable plans={plans} features={features} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("$29/mo");
    expect(container.textContent).toContain("Recommended");
    expect(container.textContent).toContain("Apps");
    expect(container.textContent).toContain("Unlimited");
  });
});
