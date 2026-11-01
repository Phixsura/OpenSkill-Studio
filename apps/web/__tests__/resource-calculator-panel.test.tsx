import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ResourceCalculatorPanel } from "@/components/resource-calculator-panel";

const est = { cpuCores: 1.5, memoryMb: 512, storageMb: 600, bandwidthGb: 5, estimatedCostCents: 2500, recommendedTier: "starter" };

describe("ResourceCalculatorPanel", () => {
  it("renders estimate", () => {
    const { container } = render(<ResourceCalculatorPanel estimate={est} />);
    expect(container.textContent).toContain("1.5 cores");
    expect(container.textContent).toContain("512 MB");
    expect(container.textContent).toContain("$25.00");
    expect(container.textContent).toContain("starter");
  });
  it("calls onCalculate", () => {
    const fn = vi.fn();
    const { getByText } = render(<ResourceCalculatorPanel estimate={null} onCalculate={fn} />);
    fireEvent.click(getByText("Calculate"));
    expect(fn).toHaveBeenCalled();
  });
});
