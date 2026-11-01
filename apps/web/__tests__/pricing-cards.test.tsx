import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingCards } from "@/components/pricing-cards";

describe("PricingCards", () => {
  it("renders plans", () => {
    const onSelect = vi.fn();
    const { container, getAllByText } = render(
      <PricingCards currentPlan="starter" onSelect={onSelect} plans={[
        { id: "free", priceDisplay: "$0/mo", apiCalls: 1000, apps: 3, teamSize: 1, features: ["basic"], isUnlimited: false },
        { id: "starter", priceDisplay: "$29/mo", apiCalls: 50000, apps: 10, teamSize: 5, features: ["basic", "webhooks"], isUnlimited: false },
        { id: "pro", priceDisplay: "$99/mo", apiCalls: 500000, apps: 50, teamSize: 25, features: ["basic", "sso"], isUnlimited: false },
        { id: "enterprise", priceDisplay: "Custom", apiCalls: -1, apps: -1, teamSize: -1, features: ["all"], isUnlimited: true },
      ]} />
    );
    expect(container.textContent).toContain("$29/mo");
    expect(container.textContent).toContain("Current Plan");
    expect(container.textContent).toContain("$99/mo");
    expect(container.textContent).toContain("Custom");
    expect(container.textContent).toContain("Unlimited");
    fireEvent.click(getAllByText("Select")[0]);
    expect(onSelect).toHaveBeenCalled();
  });
});
