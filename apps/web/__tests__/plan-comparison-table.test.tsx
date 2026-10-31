import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlanComparisonTable } from "@/components/plan-comparison-table";

describe("PlanComparisonTable", () => {
  const plans = [
    { id: "free", price_label: "Free", apps_label: "5", api_label: "1,000", support: "community" },
    { id: "pro", price_label: "$99/mo", apps_label: "Unlimited", api_label: "500,000", support: "priority" },
  ];
  const matrix = [{ feature: "webhooks", free: false, pro: true }];
  it("renders", () => {
    const { container } = render(
      <PlanComparisonTable plans={plans} featureMatrix={matrix}
        onSelect={vi.fn()} recommendedPlan="pro" />
    );
    expect(container.textContent).toContain("Compare Plans");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$99/mo");
    expect(container.textContent).toContain("⭐");
    expect(container.textContent).toContain("Unlimited");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("—");
    expect(container.textContent).toContain("Get Started");
    expect(container.textContent).toContain("Start Trial");
  });
});
