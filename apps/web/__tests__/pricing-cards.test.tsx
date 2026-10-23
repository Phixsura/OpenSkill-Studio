import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingCards } from "@/components/pricing-cards";

describe("PricingCards", () => {
  const plans = [
    { id: "free", price: 0, interval: "forever", features: ["5 apps"], featureCount: 1, recommended: false },
    { id: "pro", price: 29, interval: "monthly", features: ["Unlimited", "Support"], featureCount: 2, recommended: true },
  ];
  it("renders plans", () => {
    const { container } = render(<PricingCards plans={plans} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("free");
    expect(container.textContent).toContain("$0");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("$29");
    expect(container.textContent).toContain("Recommended");
  });
  it("select plan", () => {
    const fn = vi.fn();
    const { container } = render(<PricingCards plans={plans} onSelect={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Subscribe")!);
    expect(fn).toHaveBeenCalledWith("pro");
  });
});
