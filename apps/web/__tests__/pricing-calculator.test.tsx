import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingCalculator } from "@/components/pricing-calculator";

const tiers = [
  { name: "Free", monthlyPrice: 0, features: ["100 API calls"] },
  { name: "Pro", monthlyPrice: 29, features: ["10K API calls"], recommended: true },
];

describe("PricingCalculator", () => {
  it("renders tiers", () => {
    const { container } = render(<PricingCalculator tiers={tiers} />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$29");
    expect(container.textContent).toContain("Recommended");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { getAllByText } = render(<PricingCalculator tiers={tiers} onSelect={fn} />);
    fireEvent.click(getAllByText("Select")[1]);
    expect(fn).toHaveBeenCalledWith("Pro");
  });
});
