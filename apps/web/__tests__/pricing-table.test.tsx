import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingTable } from "@/components/pricing-table";

const plans = [
  { planId: "free", name: "Free", priceCents: 0, interval: "monthly", features: ["Basic"], trialDays: 0 },
  { planId: "pro", name: "Pro", priceCents: 999, interval: "monthly", features: ["Basic", "Advanced"], trialDays: 14 },
  { planId: "enterprise", name: "Enterprise", priceCents: 4999, interval: "monthly", features: ["All features"], trialDays: 0 },
];

describe("PricingTable", () => {
  it("renders plans", () => {
    const { container } = render(<PricingTable plans={plans} />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$9.99/mo");
    expect(container.textContent).toContain("14-day free trial");
    expect(container.textContent).toContain("Popular");
  });
  it("selects plan", () => {
    const fn = vi.fn();
    const { container } = render(<PricingTable plans={plans} onSelect={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]);
    expect(fn).toHaveBeenCalledWith("pro");
  });
});
