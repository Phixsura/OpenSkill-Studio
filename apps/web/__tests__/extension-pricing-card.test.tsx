import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionPricingCard } from "@/components/extension-pricing-card";

const mockTiers = [
  { id: "free", name: "Free", price: 0, currency: "USD", period: "free" as const,
    features: ["5 API calls/day", "Basic support"], highlighted: false, cta: "Get Started" },
  { id: "pro", name: "Pro", price: 999, currency: "USD", period: "monthly" as const,
    features: ["Unlimited API calls", "Priority support", "Custom webhooks"], highlighted: true, cta: "Subscribe" },
  { id: "enterprise", name: "Enterprise", price: 4999, currency: "USD", period: "monthly" as const,
    features: ["Everything in Pro", "SLA", "Dedicated support", "SSO"], highlighted: false, cta: "Contact Sales" },
];

describe("ExtensionPricingCard", () => {
  it("renders all tiers with prices", () => {
    const { container } = render(<ExtensionPricingCard tiers={mockTiers} extensionName="Slack Bot" />);
    expect(container.textContent).toContain("Slack Bot Plans");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$9.99");
    expect(container.textContent).toContain("$49.99");
  });

  it("shows Popular badge on highlighted tier", () => {
    const { container } = render(<ExtensionPricingCard tiers={mockTiers} extensionName="Test" />);
    expect(container.textContent).toContain("Popular");
  });

  it("renders features with checkmarks", () => {
    const { container } = render(<ExtensionPricingCard tiers={mockTiers} extensionName="Test" />);
    expect(container.textContent).toContain("Unlimited API calls");
    expect(container.textContent).toContain("SSO");
    const checks = container.querySelectorAll("li");
    expect(checks.length).toBe(9); // 2 + 3 + 4
  });

  it("calls onSelect with tier id", () => {
    const onSelect = vi.fn();
    const { getByText } = render(<ExtensionPricingCard tiers={mockTiers} extensionName="Test" onSelect={onSelect} />);
    fireEvent.click(getByText("Subscribe"));
    expect(onSelect).toHaveBeenCalledWith("pro");
  });
});
