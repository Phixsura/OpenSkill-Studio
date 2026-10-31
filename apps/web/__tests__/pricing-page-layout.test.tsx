import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingPageLayout } from "@/components/pricing-page-layout";

describe("PricingPageLayout", () => {
  const plans = [
    { id: "free", name: "Free", display_price: 0, highlighted: false, features: ["1 app"], cta: "Get Started", is_current: true, savings_pct: 0 },
    { id: "pro", name: "Pro", display_price: 9900, highlighted: true, features: ["25 apps", "SSO"], cta: "Start Trial", is_current: false, savings_pct: 0 },
  ];
  const faq = [{ q: "Can I switch?", a: "Yes!" }];
  it("renders", () => {
    const { container } = render(<PricingPageLayout plans={plans} faq={faq} trialDays={14} onSelectPlan={vi.fn()} />);
    expect(container.textContent).toContain("Simple, transparent pricing");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$99");
    expect(container.textContent).toContain("Current Plan");
    expect(container.textContent).toContain("Can I switch?");
  });
  it("select plan", () => {
    const fn = vi.fn();
    const { container } = render(<PricingPageLayout plans={plans} faq={[]} trialDays={14} onSelectPlan={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Start Trial")!);
    expect(fn).toHaveBeenCalledWith("pro");
  });
});
