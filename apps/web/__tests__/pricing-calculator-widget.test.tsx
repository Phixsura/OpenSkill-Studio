import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PricingCalculatorWidget } from "@/components/pricing-calculator-widget";

describe("PricingCalculatorWidget", () => {
  it("renders", () => {
    const calc = () => ({ totalFee: 3000, netRevenue: 7000, effectiveRate: 30, breakdown: [] });
    const { container } = render(<PricingCalculatorWidget onCalculate={calc} />);
    expect(container.textContent).toContain("Pricing Calculator");
    expect(container.textContent).toContain("$3,000");
    expect(container.textContent).toContain("$7,000");
    expect(container.textContent).toContain("30%");
    expect(container.textContent).toContain("Platform Fee");
    expect(container.textContent).toContain("You Keep");
  });
});
