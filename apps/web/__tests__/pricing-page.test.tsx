import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingPage } from "@/components/pricing-page";

describe("PricingPage", () => {
  const tiers = [
    { id: "free", name: "Free", priceDisplay: "Free", recommended: false, features: ["5 apps"], featureCount: 1 },
    { id: "pro", name: "Pro", priceDisplay: "$29/mo", recommended: true, features: ["Unlimited"], featureCount: 1 },
  ];
  const faq = [{ q: "Can I switch?", a: "Yes!" }];
  it("renders pricing page", () => {
    const { container } = render(<PricingPage tiers={tiers} faq={faq} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Simple, transparent pricing");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$29/mo");
    expect(container.textContent).toContain("Most Popular");
    expect(container.textContent).toContain("Can I switch?");
  });
});
