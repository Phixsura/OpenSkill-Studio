import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingTierCards } from "@/components/pricing-tier-cards";

describe("PricingTierCards", () => {
  const tiers = [
    { id: "free", name: "Free", price: 0, billing: "forever", features: ["5 apps"],
      highlighted: false, cta: "Get Started", annual_monthly: 0 },
    { id: "pro", name: "Pro", price: 99, billing: "/month", features: ["Unlimited"],
      highlighted: true, cta: "Start Trial", annual_monthly: 79.2 },
  ];
  it("renders", () => {
    const { container } = render(
      <PricingTierCards tiers={tiers} annual={false} recommendedId="pro"
        onSelect={vi.fn()} onToggleBilling={vi.fn()} />
    );
    expect(container.textContent).toContain("Choose Your Plan");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("✨ Recommended");
    expect(container.textContent).toContain("$99");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(
      <PricingTierCards tiers={tiers} annual={false} onSelect={fn} onToggleBilling={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Start Trial")!);
    expect(fn).toHaveBeenCalledWith("pro");
  });
});
