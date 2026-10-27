import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CostCalculatorWidget } from "@/components/cost-calculator-widget";

const plans = [
  { plan: "Free", totalCents: 1500, overageItems: 2 },
  { plan: "Pro", totalCents: 800, overageItems: 1 },
  { plan: "Enterprise", totalCents: 200, overageItems: 0 },
];

describe("CostCalculatorWidget", () => {
  it("renders calculator", () => {
    const { container } = render(<CostCalculatorWidget plans={plans} />);
    expect(container.textContent).toContain("Cost Calculator");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$15.00");
    expect(container.textContent).toContain("$8.00");
  });
  it("calculate", () => {
    const fn = vi.fn();
    const { container } = render(<CostCalculatorWidget plans={[]} onCalculate={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
