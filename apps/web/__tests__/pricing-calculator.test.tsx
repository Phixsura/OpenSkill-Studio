import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingCalculator } from "@/components/pricing-calculator";

describe("PricingCalculator", () => {
  it("renders pricing", () => {
    const onRecalc = vi.fn();
    const { container, getByText } = render(
      <PricingCalculator onRecalculate={onRecalc}
        result={{ basePrice: 29, usageCost: 10, totalDisplay: "$35.10/mo",
                   annualDisplay: "$421.20/yr", discount: 3.9 }} />
    );
    expect(container.textContent).toContain("Pricing Calculator");
    expect(container.textContent).toContain("$29.00");
    expect(container.textContent).toContain("$10.00");
    expect(container.textContent).toContain("-$3.90");
    expect(container.textContent).toContain("$35.10/mo");
    expect(container.textContent).toContain("$421.20/yr");
    fireEvent.click(getByText("Recalculate"));
    expect(onRecalc).toHaveBeenCalled();
  });
});
