import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlanComparisonPage } from "@/components/plan-comparison-page";

describe("PlanComparisonPage", () => {
  const plans = [
    { id: "free", name: "Free", priceDisplay: "Free", cta: "Get Started" },
    { id: "pro", name: "Pro", priceDisplay: "$29/mo", cta: "Try Free", recommended: true },
  ];
  const features = [{ name: "Apps", values: {
    free: { display: "5", type: "text", value: "5" },
    pro: { display: "Unlimited", type: "text", value: "Unlimited" }}}];
  it("renders comparison", () => {
    const { container } = render(
      <PlanComparisonPage plans={plans} features={features} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Choose Your Plan");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$29/mo");
    expect(container.textContent).toContain("Recommended");
    expect(container.textContent).toContain("Unlimited");
  });
});
