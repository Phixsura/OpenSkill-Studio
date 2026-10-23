import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingTableCard } from "@/components/pricing-table-card";

describe("PricingTableCard", () => {
  const plans = [
    { id: "free", label: "Free", price_cents: 0, features: ["1 app"], cta: "Get Started", highlighted: false },
    { id: "pro", label: "Pro", price_cents: 9900, features: ["25 apps", "SSO"], cta: "Start Trial", highlighted: true },
  ];
  it("renders plans", () => {
    const { container } = render(<PricingTableCard plans={plans} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$99");
    expect(container.textContent).toContain("SSO");
  });
  it("current plan", () => {
    const { container } = render(<PricingTableCard plans={plans} currentPlan="free" onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Current Plan");
  });
  it("selects plan", () => {
    const fn = vi.fn();
    const { container } = render(<PricingTableCard plans={plans} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("pro");
  });
});
